import React, { useState } from 'react';
import { 
  PlayIcon, 
  ArrowPathIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon 
} from '@heroicons/react/24/outline';
import { useApi, useAsyncAction } from '@/hooks/useApi';
import { REFRESH_INTERVALS } from '@/utils/constants';
import ApiService from '@/services/api';
import StandupSummary from './StandupSummary';
import PRReview from './PRReview';
import DocPreview from './DocPreview';
import type { TeamStandup, CodeReview } from '@/services/types';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'standup' | 'reviews' | 'docs'>('standup');
  const [selectedReview, setSelectedReview] = useState<CodeReview | null>(null);

  // API hooks
  const {
    data: standup,
    loading: standupLoading,
    error: standupError,
    refetch: refetchStandup,
  } = useApi<TeamStandup | null>(
    () => ApiService.getStandup(),
    { immediate: true, refreshInterval: REFRESH_INTERVALS.STANDUP }
  );

  const {
    execute: generateStandup,
    loading: generateStandupLoading,
    error: generateStandupError,
  } = useAsyncAction(ApiService.generateStandup);

  const {
    execute: generateReview,
    loading: generateReviewLoading,
    error: generateReviewError,
  } = useAsyncAction(ApiService.generateCodeReview);

  const {
    execute: generateDoc,
    loading: generateDocLoading,
    error: generateDocError,
  } = useAsyncAction(ApiService.generateDocstring);

  const {
    execute: generateTest,
    loading: generateTestLoading,
    error: generateTestError,
  } = useAsyncAction(ApiService.generateTest);

  const {
    execute: aggregateActivity,
    loading: aggregateLoading,
    error: aggregateError,
  } = useAsyncAction(ApiService.aggregateActivity);

  // Handlers
  const handleGenerateStandup = async () => {
    const result = await generateStandup(24);
    if (result) {
      await refetchStandup();
    }
  };

  const handleGenerateReview = async (prNumber?: number) => {
    const result = await generateReview(prNumber, 24);
    if (result && result.length > 0) {
      setSelectedReview(result[0]);
      setActiveTab('reviews');
    }
  };

  const handleGenerateDoc = async (filePath: string, functionName: string, code: string) => {
    await generateDoc(filePath, functionName, code);
  };

  const handleGenerateTest = async (filePath: string, functionName: string, code: string) => {
    await generateTest(filePath, functionName, code);
  };

  const handleAggregateActivity = async () => {
    await aggregateActivity(24);
  };

  const tabs = [
    { id: 'standup', name: 'Standup', icon: '🚀' },
    { id: 'reviews', name: 'Reviews', icon: '📝' },
    { id: 'docs', name: 'Docs & Tests', icon: '📚' },
  ] as const;

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button
            onClick={handleGenerateStandup}
            disabled={generateStandupLoading}
            className="btn-primary disabled:opacity-50 flex items-center justify-center"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            {generateStandupLoading ? 'Generating...' : 'Generate Standup'}
          </button>
          
          <button
            onClick={() => handleGenerateReview()}
            disabled={generateReviewLoading}
            className="btn-secondary disabled:opacity-50 flex items-center justify-center"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            {generateReviewLoading ? 'Reviewing...' : 'Review Recent PRs'}
          </button>
          
          <button
            onClick={handleAggregateActivity}
            disabled={aggregateLoading}
            className="btn-secondary disabled:opacity-50 flex items-center justify-center"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            {aggregateLoading ? 'Syncing...' : 'Sync GitHub Data'}
          </button>
          
          <button
            onClick={() => setActiveTab('docs')}
            className="btn-secondary flex items-center justify-center"
          >
            <PlayIcon className="h-4 w-4 mr-2" />
            Generate Docs/Tests
          </button>
        </div>

        {/* Error Messages */}
        {(generateStandupError || generateReviewError || aggregateError) && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 flex-shrink-0" />
              <div className="text-sm text-red-700">
                {generateStandupError || generateReviewError || aggregateError}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'standup' && (
          <div>
            {standupError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 flex-shrink-0" />
                  <div className="text-sm text-red-700">{standupError}</div>
                </div>
              </div>
            )}
            
            {standup ? (
              <StandupSummary
                standup={standup}
                onRefresh={refetchStandup}
                loading={standupLoading}
              />
            ) : standupLoading ? (
              <div className="card text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-500">Loading standup summary...</p>
              </div>
            ) : (
              <div className="card text-center py-8">
                <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Standup Available</h3>
                <p className="text-gray-500 mb-4">
                  Generate a new standup summary from recent GitHub activity.
                </p>
                <button
                  onClick={handleGenerateStandup}
                  disabled={generateStandupLoading}
                  className="btn-primary disabled:opacity-50"
                >
                  {generateStandupLoading ? 'Generating...' : 'Generate Standup'}
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'reviews' && (
          <div>
            {generateReviewError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 flex-shrink-0" />
                  <div className="text-sm text-red-700">{generateReviewError}</div>
                </div>
              </div>
            )}
            
            {selectedReview ? (
              <PRReview
                review={selectedReview}
                onRefresh={() => handleGenerateReview(selectedReview.pr_number)}
                loading={generateReviewLoading}
              />
            ) : (
              <div className="card text-center py-8">
                <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Reviews Available</h3>
                <p className="text-gray-500 mb-4">
                  Generate AI-powered code reviews for recent pull requests.
                </p>
                <button
                  onClick={() => handleGenerateReview()}
                  disabled={generateReviewLoading}
                  className="btn-primary disabled:opacity-50"
                >
                  {generateReviewLoading ? 'Reviewing...' : 'Review Recent PRs'}
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'docs' && (
          <div>
            {(generateDocError || generateTestError) && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2 flex-shrink-0" />
                  <div className="text-sm text-red-700">
                    {generateDocError || generateTestError}
                  </div>
                </div>
              </div>
            )}
            
            <DocPreview
              onGenerateDoc={handleGenerateDoc}
              onGenerateTest={handleGenerateTest}
              loading={generateDocLoading || generateTestLoading}
            />
          </div>
        )}
      </div>
    </div>
  );
}