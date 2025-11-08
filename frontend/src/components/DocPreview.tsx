import React, { useState } from 'react';
import { 
  DocumentTextIcon, 
  BeakerIcon, 
  ClipboardDocumentIcon,
  CheckIcon 
} from '@heroicons/react/24/outline';
import type { DocstringGeneration, TestGeneration } from '@/services/types';

interface DocPreviewProps {
  onGenerateDoc: (filePath: string, functionName: string, code: string) => Promise<void>;
  onGenerateTest: (filePath: string, functionName: string, code: string) => Promise<void>;
  loading?: boolean;
}

export default function DocPreview({ onGenerateDoc, onGenerateTest, loading }: DocPreviewProps) {
  const [formData, setFormData] = useState({
    filePath: '',
    functionName: '',
    code: '',
  });
  const [generatedDoc, setGeneratedDoc] = useState<DocstringGeneration | null>(null);
  const [generatedTest, setGeneratedTest] = useState<TestGeneration | null>(null);
  const [copiedDoc, setCopiedDoc] = useState(false);
  const [copiedTest, setCopiedTest] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleGenerateDoc = async () => {
    if (!formData.filePath || !formData.functionName || !formData.code) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const result = await onGenerateDoc(formData.filePath, formData.functionName, formData.code);
      // The result would be set by the parent component through a callback or state management
    } catch (error) {
      console.error('Failed to generate documentation:', error);
    }
  };

  const handleGenerateTest = async () => {
    if (!formData.filePath || !formData.functionName || !formData.code) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const result = await onGenerateTest(formData.filePath, formData.functionName, formData.code);
      // The result would be set by the parent component through a callback or state management
    } catch (error) {
      console.error('Failed to generate test:', error);
    }
  };

  const copyToClipboard = async (text: string, type: 'doc' | 'test') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'doc') {
        setCopiedDoc(true);
        setTimeout(() => setCopiedDoc(false), 2000);
      } else {
        setCopiedTest(true);
        setTimeout(() => setCopiedTest(false), 2000);
      }
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Documentation & Tests</h2>
        <p className="text-sm text-gray-500 mt-1">
          Generate AI-powered docstrings and unit tests for your code
        </p>
      </div>

      {/* Input Form */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Code Input</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="filePath" className="block text-sm font-medium text-gray-700 mb-1">
              File Path
            </label>
            <input
              type="text"
              id="filePath"
              className="input-field"
              placeholder="e.g., src/utils/math.py"
              value={formData.filePath}
              onChange={(e) => handleInputChange('filePath', e.target.value)}
            />
          </div>
          
          <div>
            <label htmlFor="functionName" className="block text-sm font-medium text-gray-700 mb-1">
              Function Name
            </label>
            <input
              type="text"
              id="functionName"
              className="input-field"
              placeholder="e.g., calculate_factorial"
              value={formData.functionName}
              onChange={(e) => handleInputChange('functionName', e.target.value)}
            />
          </div>
        </div>

        <div className="mb-4">
          <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
            Function Code
          </label>
          <textarea
            id="code"
            rows={8}
            className="input-field font-mono text-sm"
            placeholder="def calculate_factorial(n):
    if n < 0:
        raise ValueError('Factorial is not defined for negative numbers')
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result"
            value={formData.code}
            onChange={(e) => handleInputChange('code', e.target.value)}
          />
        </div>

        <div className="flex space-x-4">
          <button
            onClick={handleGenerateDoc}
            disabled={loading}
            className="btn-primary disabled:opacity-50 flex items-center"
          >
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            {loading ? 'Generating...' : 'Generate Docstring'}
          </button>
          
          <button
            onClick={handleGenerateTest}
            disabled={loading}
            className="btn-secondary disabled:opacity-50 flex items-center"
          >
            <BeakerIcon className="h-4 w-4 mr-2" />
            {loading ? 'Generating...' : 'Generate Test'}
          </button>
        </div>
      </div>

      {/* Generated Documentation */}
      {generatedDoc && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <DocumentTextIcon className="h-5 w-5 mr-2 text-blue-600" />
              Generated Docstring ({generatedDoc.style} style)
            </h3>
            <button
              onClick={() => copyToClipboard(generatedDoc.generated_docstring, 'doc')}
              className="btn-secondary text-sm flex items-center"
            >
              {copiedDoc ? (
                <>
                  <CheckIcon className="h-4 w-4 mr-1 text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                  Copy
                </>
              )}
            </button>
          </div>
          
          <div className="bg-gray-50 rounded-md p-4 border">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto">
              <code>{generatedDoc.generated_docstring}</code>
            </pre>
          </div>
          
          <div className="mt-3 text-sm text-gray-600">
            <p><strong>Function:</strong> {generatedDoc.function_name}</p>
            <p><strong>File:</strong> {generatedDoc.file_path}</p>
          </div>
        </div>
      )}

      {/* Generated Test */}
      {generatedTest && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <BeakerIcon className="h-5 w-5 mr-2 text-green-600" />
              Generated Unit Test ({generatedTest.test_framework})
            </h3>
            <button
              onClick={() => copyToClipboard(generatedTest.generated_test, 'test')}
              className="btn-secondary text-sm flex items-center"
            >
              {copiedTest ? (
                <>
                  <CheckIcon className="h-4 w-4 mr-1 text-green-600" />
                  Copied!
                </>
              ) : (
                <>
                  <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                  Copy
                </>
              )}
            </button>
          </div>
          
          <div className="bg-gray-50 rounded-md p-4 border">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto">
              <code>{generatedTest.generated_test}</code>
            </pre>
          </div>
          
          <div className="mt-3 text-sm text-gray-600 flex justify-between">
            <div>
              <p><strong>Function:</strong> {generatedTest.function_name}</p>
              <p><strong>File:</strong> {generatedTest.file_path}</p>
            </div>
            {generatedTest.coverage_estimate && (
              <div className="text-right">
                <p><strong>Estimated Coverage:</strong> {generatedTest.coverage_estimate}%</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Example Code */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-medium text-blue-900 mb-3">💡 Example Usage</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p><strong>1.</strong> Paste your function code in the text area above</p>
          <p><strong>2.</strong> Specify the file path and function name</p>
          <p><strong>3.</strong> Click "Generate Docstring" or "Generate Test"</p>
          <p><strong>4.</strong> Copy the generated content to your codebase</p>
        </div>
      </div>
    </div>
  );
}