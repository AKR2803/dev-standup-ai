import React from 'react';
import { format } from 'date-fns';
import { 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  CodeBracketIcon 
} from '@heroicons/react/24/outline';
import { SEVERITY_COLORS, SEVERITY_LABELS } from '@/utils/constants';
import type { CodeReview, ReviewFinding } from '@/services/types';
import clsx from 'clsx';

interface PRReviewProps {
  review: CodeReview;
  onRefresh?: () => void;
  loading?: boolean;
}

export default function PRReview({ review, onRefresh, loading }: PRReviewProps) {
  const reviewDate = new Date(review.timestamp);
  const scoreColor = review.overall_score >= 8 ? 'text-green-600' : 
                    review.overall_score >= 6 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            PR #{review.pr_number}: {review.pr_title}
          </h2>
          <p className="text-sm text-gray-500">
            Reviewed by {review.reviewer} on {format(reviewDate, 'MMM d, yyyy \'at\' h:mm a')}
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

      {/* Review Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <span className="text-sm font-medium text-gray-500 mr-2">Overall Score:</span>
              <span className={clsx('text-2xl font-bold', scoreColor)}>
                {review.overall_score}/10
              </span>
            </div>
            <div className="flex items-center">
              {review.approved ? (
                <CheckCircleIcon className="h-6 w-6 text-green-500 mr-2" />
              ) : (
                <XCircleIcon className="h-6 w-6 text-red-500 mr-2" />
              )}
              <span className={clsx('font-medium', review.approved ? 'text-green-700' : 'text-red-700')}>
                {review.approved ? 'Approved' : 'Changes Requested'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Summary</h3>
          <p className="text-gray-700">{review.summary}</p>
        </div>

        {/* Issue Counts */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{review.critical_issues}</div>
            <div className="text-sm text-gray-500">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{review.high_issues}</div>
            <div className="text-sm text-gray-500">High</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{review.findings.length}</div>
            <div className="text-sm text-gray-500">Total Issues</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{review.suggestions.length}</div>
            <div className="text-sm text-gray-500">Suggestions</div>
          </div>
        </div>
      </div>

      {/* Suggestions */}
      {review.suggestions.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center">
            <LightBulbIcon className="h-5 w-5 mr-2 text-yellow-500" />
            Suggestions
          </h3>
          <ul className="space-y-2">
            {review.suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="text-yellow-500 mr-2">💡</span>
                <span className="text-gray-700">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Findings */}
      {review.findings.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Detailed Findings</h3>
          {review.findings.map((finding, index) => (
            <FindingCard key={index} finding={finding} />
          ))}
        </div>
      )}

      {/* No Issues */}
      {review.findings.length === 0 && (
        <div className="card text-center py-8">
          <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Issues Found</h3>
          <p className="text-gray-500">This pull request looks great! No issues were detected.</p>
        </div>
      )}
    </div>
  );
}

interface FindingCardProps {
  finding: ReviewFinding;
}

function FindingCard({ finding }: FindingCardProps) {
  const severityClass = SEVERITY_COLORS[finding.severity];
  const severityLabel = SEVERITY_LABELS[finding.severity];

  return (
    <div className="card border-l-4 border-l-gray-300">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <span className={clsx('px-2 py-1 rounded-full text-xs font-medium', severityClass)}>
            {severityLabel}
          </span>
          <span className="text-sm font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
            {finding.category}
          </span>
        </div>
        <div className="text-sm text-gray-500">
          {finding.file_path}
          {finding.line_number && `:${finding.line_number}`}
        </div>
      </div>

      <div className="mb-3">
        <p className="text-gray-900 font-medium mb-1">{finding.message}</p>
        {finding.suggestion && (
          <p className="text-gray-700 text-sm">
            <span className="font-medium">Suggestion:</span> {finding.suggestion}
          </p>
        )}
      </div>

      {finding.code_snippet && (
        <div className="bg-gray-50 rounded-md p-3 border">
          <div className="flex items-center mb-2">
            <CodeBracketIcon className="h-4 w-4 text-gray-500 mr-2" />
            <span className="text-sm font-medium text-gray-700">Code Snippet</span>
          </div>
          <pre className="text-sm text-gray-800 overflow-x-auto">
            <code>{finding.code_snippet}</code>
          </pre>
        </div>
      )}
    </div>
  );
}