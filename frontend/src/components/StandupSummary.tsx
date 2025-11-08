import React from 'react';
import { format } from 'date-fns';
import { 
  UserGroupIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';
import type { TeamStandup, StandupItem } from '@/services/types';

interface StandupSummaryProps {
  standup: TeamStandup;
  onRefresh?: () => void;
  loading?: boolean;
}

export default function StandupSummary({ standup, onRefresh, loading }: StandupSummaryProps) {
  const standupDate = new Date(standup.date);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Team Standup</h2>
          <p className="text-sm text-gray-500">
            {format(standupDate, 'EEEE, MMMM d, yyyy')}
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="btn-primary disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-primary-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Team Members</p>
              <p className="text-2xl font-semibold text-gray-900">{standup.total_developers}</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">With Blockers</p>
              <p className="text-2xl font-semibold text-gray-900">{standup.developers_with_blockers}</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Key Highlights</p>
              <p className="text-2xl font-semibold text-gray-900">{standup.key_highlights.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Team Summary */}
      {standup.summary && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Team Summary</h3>
          <p className="text-gray-700">{standup.summary}</p>
        </div>
      )}

      {/* Key Highlights */}
      {standup.key_highlights.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-3">🎯 Key Highlights</h3>
          <ul className="space-y-2">
            {standup.key_highlights.map((highlight, index) => (
              <li key={index} className="flex items-start">
                <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                <span className="text-gray-700">{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Team Blockers */}
      {standup.team_blockers.length > 0 && (
        <div className="card border-l-4 border-l-orange-500">
          <h3 className="text-lg font-medium text-gray-900 mb-3">🚧 Team Blockers</h3>
          <ul className="space-y-2">
            {standup.team_blockers.map((blocker, index) => (
              <li key={index} className="flex items-start">
                <ExclamationTriangleIcon className="h-5 w-5 text-orange-500 mt-0.5 mr-2 flex-shrink-0" />
                <span className="text-gray-700">{blocker}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Individual Developer Updates */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Individual Updates</h3>
        {standup.team_items.map((item, index) => (
          <DeveloperStandupCard key={index} item={item} />
        ))}
      </div>
    </div>
  );
}

interface DeveloperStandupCardProps {
  item: StandupItem;
}

function DeveloperStandupCard({ item }: DeveloperStandupCardProps) {
  return (
    <div className="card">
      <div className="flex items-center mb-4">
        <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
          <span className="text-primary-600 font-medium text-sm">
            {item.developer.split(' ').map(n => n[0]).join('').toUpperCase()}
          </span>
        </div>
        <div className="ml-3">
          <h4 className="text-lg font-medium text-gray-900">{item.developer}</h4>
          {item.mood && (
            <span className="text-sm text-gray-500">Mood: {item.mood}</span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Yesterday */}
        <div>
          <h5 className="text-sm font-medium text-gray-500 mb-2 flex items-center">
            <CheckCircleIcon className="h-4 w-4 mr-1" />
            Yesterday
          </h5>
          {item.yesterday.length > 0 ? (
            <ul className="space-y-1">
              {item.yesterday.map((task, index) => (
                <li key={index} className="text-sm text-gray-700">• {task}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-400 italic">No updates</p>
          )}
        </div>

        {/* Today */}
        <div>
          <h5 className="text-sm font-medium text-gray-500 mb-2 flex items-center">
            <ClockIcon className="h-4 w-4 mr-1" />
            Today
          </h5>
          {item.today.length > 0 ? (
            <ul className="space-y-1">
              {item.today.map((task, index) => (
                <li key={index} className="text-sm text-gray-700">• {task}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-400 italic">No plans</p>
          )}
        </div>

        {/* Blockers */}
        <div>
          <h5 className="text-sm font-medium text-gray-500 mb-2 flex items-center">
            <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
            Blockers
          </h5>
          {item.blockers.length > 0 ? (
            <ul className="space-y-1">
              {item.blockers.map((blocker, index) => (
                <li key={index} className="text-sm text-orange-700 bg-orange-50 px-2 py-1 rounded">
                  • {blocker}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-green-600 italic">No blockers</p>
          )}
        </div>
      </div>
    </div>
  );
}