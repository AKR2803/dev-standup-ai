// API Configuration
const API_BASE_URL = 'https://ymx4dqjcua.execute-api.us-east-1.amazonaws.com/dev/api';

// API Service Class
class ApiService {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            console.log(`API Request: ${config.method || 'GET'} ${url}`);
            const response = await fetch(url, config);
            
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                let errorMessage;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || `HTTP ${response.status}: ${response.statusText}`;
                } catch {
                    const errorText = await response.text();
                    console.error('Error response text:', errorText);
                    errorMessage = errorText || `HTTP ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }
            
            const responseText = await response.text();
            console.log('Response text:', responseText);
            
            if (!responseText.trim()) {
                throw new Error('Empty response from server');
            }
            
            try {
                return JSON.parse(responseText);
            } catch (parseError) {
                console.error('JSON Parse Error:', parseError);
                console.error('Raw response:', responseText);
                console.error('Response length:', responseText.length);
                console.error('First 100 chars:', responseText.substring(0, 100));
                throw new Error(`Invalid JSON response: ${parseError.message}`);
            }
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    static async getStandup() {
        return this.request('/standup');
    }

    static async generateStandup(hours = 24) {
        return this.request(`/standup/generate?hours=${hours}`, { method: 'POST' });
    }

    static async syncGitHub(hours = 24) {
        return this.request(`/github/sync?hours=${hours}`, { method: 'POST' });
    }

    static async generateDocs(filePath, branch = 'main') {
        return this.request('/docs/generate', {
            method: 'POST',
            body: JSON.stringify({ file_path: filePath, branch })
        });
    }

    static async generateTests(filePath, branch = 'main') {
        return this.request('/tests/generate', {
            method: 'POST',
            body: JSON.stringify({ file_path: filePath, branch })
        });
    }

    static async sendToSlack(standupData) {
        return this.request('/slack/post', {
            method: 'POST',
            body: JSON.stringify({ standup: standupData })
        });
    }

    static async generateReview(prNumber = null, hours = 24) {
        const params = new URLSearchParams();
        params.append('hours', hours.toString());
        if (prNumber) {
            params.append('pr_number', prNumber.toString());
        }
        return this.request(`/reviews/generate?${params}`, { method: 'POST' });
    }

    static async healthCheck() {
        return this.request('/health');
    }
}

// UI Manager Class
class UIManager {
    constructor() {
        this.currentPage = 'home-page';
        this.currentRepo = 'dev-standup-ai';
        this.lastSyncTime = null;
        this.standupData = null;
        
        this.initializeEventListeners();
        this.checkAPIHealth();
        this.loadHomePage();
    }

    initializeEventListeners() {
        // Navigation
        document.getElementById('back-to-home').addEventListener('click', () => this.showPage('home-page'));
        document.getElementById('back-to-sync').addEventListener('click', () => this.showPage('sync-page'));
        document.getElementById('back-to-sync-docs').addEventListener('click', () => this.showPage('sync-page'));
        document.getElementById('back-to-sync-tests').addEventListener('click', () => this.showPage('sync-page'));
        document.getElementById('back-to-sync-review').addEventListener('click', () => this.showPage('sync-page'));

        // Home page
        document.getElementById('refresh-btn').addEventListener('click', () => this.loadHomePage());

        // Sync page
        document.getElementById('sync-now-btn').addEventListener('click', () => this.syncRepository());
        document.getElementById('generate-standup-btn').addEventListener('click', () => this.generateStandup());
        document.getElementById('generate-docs-btn').addEventListener('click', () => this.showPage('docstring-page'));
        document.getElementById('generate-tests-btn').addEventListener('click', () => this.showPage('tests-page'));
        document.getElementById('generate-review-btn').addEventListener('click', () => this.showPage('review-page'));

        // Standup page
        document.getElementById('send-to-slack-btn').addEventListener('click', () => this.sendToSlack());

        // Docstring page
        document.getElementById('generate-docs-submit').addEventListener('click', () => this.generateDocstring());

        // Tests page
        document.getElementById('generate-tests-submit').addEventListener('click', () => this.generateTestCases());

        // Review page
        document.getElementById('generate-review-submit').addEventListener('click', () => this.generatePRReview());
    }

    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show target page
        document.getElementById(pageId).classList.add('active');
        this.currentPage = pageId;
    }

    showLoading(containerId, show = true) {
        const container = document.getElementById(containerId);
        if (show) {
            container.classList.remove('hidden');
        } else {
            container.classList.add('hidden');
        }
    }

    showResult(containerId, show = true) {
        const container = document.getElementById(containerId);
        if (show) {
            container.classList.remove('hidden');
        } else {
            container.classList.add('hidden');
        }
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.getElementById('toast-container').appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    async loadHomePage() {
        this.showLoading('loading-repos', true);
        
        try {
            // Simulate repo data since we don't have a repos endpoint
            const repoData = [{
                name: 'dev-standup-ai',
                lastSync: this.lastSyncTime,
                owner: 'AKR2803'
            }];
            
            this.populateRepoTable(repoData);
        } catch (error) {
            this.showToast(`Failed to load repositories: ${error.message}`, 'error');
        } finally {
            this.showLoading('loading-repos', false);
        }
    }

    populateRepoTable(repos) {
        const tbody = document.getElementById('repo-table-body');
        tbody.innerHTML = '';
        
        repos.forEach(repo => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="repo-name">${repo.name}</div>
                    <div class="repo-owner">${repo.owner}</div>
                </td>
                <td>
                    <div class="sync-time ${repo.lastSync ? '' : 'never'}">
                        ${repo.lastSync ? new Date(repo.lastSync).toLocaleString() : 'Never'}
                    </div>
                </td>
                <td>
                    <button class="btn btn-primary sync-btn" data-repo="${repo.name}">
                        Sync & Actions
                    </button>
                </td>
            `;
            
            row.querySelector('.sync-btn').addEventListener('click', () => {
                this.currentRepo = repo.name;
                this.showSyncPage(repo);
            });
            
            tbody.appendChild(row);
        });
    }

    showSyncPage(repo) {
        document.getElementById('sync-repo-name').textContent = `${repo.name} - Sync & Actions`;
        document.getElementById('last-sync-time').textContent = 
            `Last sync: ${repo.lastSync ? new Date(repo.lastSync).toLocaleString() : 'Never'}`;
        
        // Update sync button text and help text based on sync status
        const syncBtn = document.getElementById('sync-now-btn');
        const helpText = document.getElementById('sync-help-text');
        const hasPreviousSync = repo.lastSync || this.lastSyncTime;
        
        syncBtn.textContent = hasPreviousSync ? 'Re-sync' : 'Sync Now';
        helpText.textContent = hasPreviousSync ? 
            'Re-sync to get latest changes from GitHub' : 
            'Sync is required before using actions';
        
        // Show actions if previously synced, hide only if never synced
        if (hasPreviousSync) {
            document.getElementById('sync-actions').classList.remove('hidden');
        } else {
            document.getElementById('sync-actions').classList.add('hidden');
        }
        
        this.showPage('sync-page');
    }

    async syncRepository() {
        const syncBtn = document.getElementById('sync-now-btn');
        const wasFirstSync = !this.lastSyncTime;
        
        syncBtn.disabled = true;
        syncBtn.textContent = 'Syncing...';
        
        try {
            const result = await ApiService.syncGitHub(24);
            this.lastSyncTime = new Date().toISOString();
            
            document.getElementById('last-sync-time').textContent = 
                `Last sync: ${new Date(this.lastSyncTime).toLocaleString()}`;
            
            // Show action buttons after sync
            document.getElementById('sync-actions').classList.remove('hidden');
            
            if (wasFirstSync) {
                this.showToast('Repository synced successfully! You can now use the actions below.');
            } else {
                this.showToast('Repository re-synced successfully!');
            }
        } catch (error) {
            this.showToast(`Sync failed: ${error.message}`, 'error');
        } finally {
            syncBtn.disabled = false;
            syncBtn.textContent = wasFirstSync ? 'Sync Now' : 'Re-sync';
        }
    }

    async generateStandup() {
        this.showPage('standup-page');
        this.showLoading('standup-loading', true);
        this.showResult('standup-result', false);
        
        try {
            const response = await ApiService.generateStandup(24);
            this.standupData = response;
            this.displayStandup(response);
        } catch (error) {
            this.showToast(`Failed to generate standup: ${error.message}`, 'error');
            this.showPage('sync-page');
        } finally {
            this.showLoading('standup-loading', false);
        }
    }

    displayStandup(standup) {
        // Summary
        document.getElementById('standup-summary-text').textContent = 
            standup.summary || 'No summary available';
        
        // Highlights
        const highlightsList = document.getElementById('standup-highlights-list');
        highlightsList.innerHTML = '';
        (standup.key_highlights || []).forEach(highlight => {
            const li = document.createElement('li');
            li.textContent = highlight;
            highlightsList.appendChild(li);
        });
        
        // Team items
        const itemsContainer = document.getElementById('standup-items-container');
        itemsContainer.innerHTML = '';
        (standup.team_items || []).forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'standup-item';
            itemDiv.innerHTML = `
                <h4>👤 ${item.developer}</h4>
                <div class="standup-section">
                    <strong>Yesterday:</strong>
                    <ul>
                        ${item.yesterday.map(task => `<li>${task}</li>`).join('')}
                    </ul>
                </div>
                <div class="standup-section">
                    <strong>Today:</strong>
                    <ul>
                        ${item.today.map(task => `<li>${task}</li>`).join('')}
                    </ul>
                </div>
                ${item.blockers.length > 0 ? `
                <div class="standup-section">
                    <strong>Blockers:</strong>
                    <ul>
                        ${item.blockers.map(blocker => `<li>${blocker}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
            `;
            itemsContainer.appendChild(itemDiv);
        });
        
        this.showResult('standup-result', true);
    }

    async sendToSlack() {
        if (!this.standupData) {
            this.showToast('No standup data to send', 'error');
            return;
        }
        
        const slackBtn = document.getElementById('send-to-slack-btn');
        slackBtn.disabled = true;
        slackBtn.textContent = 'Sending...';
        
        try {
            await ApiService.sendToSlack(this.standupData);
            this.showToast('Standup sent to Slack successfully!');
        } catch (error) {
            console.error('Slack error details:', error);
            // Check if it's actually successful but API returns error format
            if (error.message.includes('200') || error.message.includes('ok')) {
                this.showToast('Standup sent to Slack successfully!');
            } else {
                this.showToast(`Failed to send to Slack: ${error.message}`, 'error');
            }
        } finally {
            slackBtn.disabled = false;
            slackBtn.innerHTML = '<span class="icon">💬</span> Send to Slack';
        }
    }

    async generateDocstring() {
        const filePath = document.getElementById('file-path-input').value.trim();
        const branch = document.getElementById('docs-branch-input').value.trim() || 'main';
        
        if (!filePath) {
            this.showToast('Please enter a file path', 'error');
            return;
        }
        
        this.showLoading('docstring-loading', true);
        this.showResult('docstring-result', false);
        
        try {
            const response = await ApiService.generateDocs(filePath, branch);
            this.displayDocstring(response);
        } catch (error) {
            console.error('Docstring error:', error);
            this.showToast(`Failed to generate docstring: ${error.message}`, 'error');
        } finally {
            this.showLoading('docstring-loading', false);
        }
    }

    displayDocstring(docData) {
        document.getElementById('original-code').textContent = docData.original_code || 'No original code available';
        document.getElementById('generated-docstring').textContent = docData.generated_docstring || 'No docstring generated';
        
        this.showResult('docstring-result', true);
    }

    async generateTestCases() {
        const filePath = document.getElementById('test-file-path-input').value.trim();
        const branch = document.getElementById('tests-branch-input').value.trim() || 'main';
        
        if (!filePath) {
            this.showToast('Please enter a file path', 'error');
            return;
        }
        
        this.showLoading('tests-loading', true);
        this.showResult('tests-result', false);
        
        try {
            const response = await ApiService.generateTests(filePath, branch);
            this.displayTests(response);
        } catch (error) {
            console.error('Tests error:', error);
            this.showToast(`Failed to generate tests: ${error.message}`, 'error');
        } finally {
            this.showLoading('tests-loading', false);
        }
    }

    displayTests(testData) {
        document.getElementById('test-framework').textContent = 
            `Framework: ${testData.test_framework || 'Unknown'}`;
        document.getElementById('coverage-estimate').textContent = 
            `Estimated Coverage: ${testData.coverage_estimate || 'N/A'}%`;
        document.getElementById('generated-tests').textContent = 
            testData.generated_test || 'No tests generated';
        
        this.showResult('tests-result', true);
    }

    async generatePRReview() {
        const prNumber = document.getElementById('pr-number-input').value.trim();
        const hours = parseInt(document.getElementById('review-hours-input').value) || 24;
        
        this.showLoading('review-loading', true);
        this.showResult('review-result', false);
        
        try {
            const response = await ApiService.generateReview(prNumber || null, hours);
            this.displayPRReview(response);
        } catch (error) {
            console.error('PR Review error:', error);
            this.showToast(`Failed to generate PR review: ${error.message}`, 'error');
        } finally {
            this.showLoading('review-loading', false);
        }
    }

    displayPRReview(reviewData) {
        // Handle both single review and multiple reviews
        const reviews = reviewData.reviews || [reviewData];
        
        // Check if we have any reviews
        if (!reviews || reviews.length === 0 || !reviews[0] || !reviews[0].pr_number) {
            // Show message for no reviews found
            const findingsContainer = document.getElementById('review-findings-container');
            findingsContainer.innerHTML = '<div class="no-reviews-message"><h3>No Pull Requests Found</h3><p>No pull requests were found in the specified time range or the PR number doesn\'t exist.</p><p>Try:</p><ul><li>Increasing the hours to look back</li><li>Checking if the PR number exists</li><li>Creating some pull requests first</li></ul></div>';
            
            document.getElementById('review-title').textContent = 'No Reviews Available';
            document.getElementById('review-score').textContent = '';
            document.getElementById('review-summary-text').textContent = reviewData.message || 'No pull requests found to review';
            document.getElementById('review-suggestions-list').innerHTML = '<li>Create some pull requests to get started with reviews</li>';
            
            this.showResult('review-result', true);
            return;
        }
        
        const review = reviews[0]; // Display first review for now
        
        // Review header
        document.getElementById('review-title').textContent = `PR #${review.pr_number}: ${review.pr_title}`;
        
        // Score with color coding
        const scoreElement = document.getElementById('review-score');
        scoreElement.textContent = `${review.overall_score}/10`;
        scoreElement.className = 'review-score ' + 
            (review.overall_score >= 8 ? 'high' : review.overall_score >= 6 ? 'medium' : 'low');
        
        // Summary
        document.getElementById('review-summary-text').textContent = review.summary || 'No summary available';
        
        // Findings
        const findingsContainer = document.getElementById('review-findings-container');
        findingsContainer.innerHTML = '';
        
        if (review.findings && review.findings.length > 0) {
            review.findings.forEach(finding => {
                const findingDiv = document.createElement('div');
                findingDiv.className = `finding-item ${finding.severity}`;
                findingDiv.innerHTML = `
                    <div class="finding-header">
                        <span class="finding-file">${finding.file_path}${finding.line_number ? `:${finding.line_number}` : ''}</span>
                        <span class="finding-severity ${finding.severity}">${finding.severity}</span>
                    </div>
                    <div class="finding-message">${finding.message}</div>
                    ${finding.suggestion ? `<div class="finding-suggestion">💡 ${finding.suggestion}</div>` : ''}
                `;
                findingsContainer.appendChild(findingDiv);
            });
        } else {
            findingsContainer.innerHTML = '<p>No issues found! 🎉</p>';
        }
        
        // Suggestions
        const suggestionsList = document.getElementById('review-suggestions-list');
        suggestionsList.innerHTML = '';
        
        if (review.suggestions && review.suggestions.length > 0) {
            review.suggestions.forEach(suggestion => {
                const li = document.createElement('li');
                li.textContent = suggestion;
                suggestionsList.appendChild(li);
            });
        } else {
            suggestionsList.innerHTML = '<li>No additional suggestions</li>';
        }
        
        this.showResult('review-result', true);
    }

    async checkAPIHealth() {
        try {
            console.log('Checking API health...');
            const health = await ApiService.healthCheck();
            console.log('API Health Check:', health);
            this.showToast('API connection successful', 'success');
        } catch (error) {
            console.error('API Health Check Failed:', error);
            this.showToast(`API connection failed: ${error.message}`, 'error');
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new UIManager();
});