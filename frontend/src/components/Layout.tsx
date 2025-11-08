import React from 'react';
import { Bars3Icon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-gray-900">
                  DevStandup.ai
                </h1>
              </div>
              <div className="hidden md:ml-6 md:flex md:space-x-8">
                <a
                  href="#dashboard"
                  className="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-primary-500 text-sm font-medium"
                >
                  Dashboard
                </a>
                <a
                  href="#standup"
                  className="text-gray-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium"
                >
                  Standups
                </a>
                <a
                  href="#reviews"
                  className="text-gray-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium"
                >
                  Reviews
                </a>
                <a
                  href="#docs"
                  className="text-gray-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium"
                >
                  Docs & Tests
                </a>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                type="button"
                className="text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <span className="sr-only">View notifications</span>
                <BellIcon className="h-6 w-6" aria-hidden="true" />
              </button>
              <button
                type="button"
                className="text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <span className="sr-only">View profile</span>
                <UserCircleIcon className="h-6 w-6" aria-hidden="true" />
              </button>
              <button
                type="button"
                className="md:hidden text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <span className="sr-only">Open menu</span>
                <Bars3Icon className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2023 DevStandup.ai. Powered by Claude AI.
            </p>
            <div className="flex space-x-6">
              <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
                Documentation
              </a>
              <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
                Support
              </a>
              <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}