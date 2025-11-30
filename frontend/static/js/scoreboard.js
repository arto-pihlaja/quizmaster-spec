/**
 * Scoreboard JavaScript - QuizMaster
 * Handles refresh, pagination, and jump-to-rank functionality
 */

(function() {
    'use strict';

    // DOM Elements
    const refreshBtn = document.getElementById('refresh-btn');
    const jumpToRankBtn = document.getElementById('jump-to-rank-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorDisplay = document.getElementById('error-display');
    const scoreboardBody = document.getElementById('scoreboard-body');
    const scoreboardTable = document.getElementById('scoreboard-table');

    // State from server
    const state = window.scoreboardState || {};

    /**
     * Show loading indicator
     */
    function showLoading() {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
        if (refreshBtn) {
            refreshBtn.disabled = true;
        }
    }

    /**
     * Hide loading indicator
     */
    function hideLoading() {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        if (refreshBtn) {
            refreshBtn.disabled = false;
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        if (errorDisplay) {
            errorDisplay.textContent = message;
            errorDisplay.style.display = 'block';
        }
    }

    /**
     * Hide error message
     */
    function hideError() {
        if (errorDisplay) {
            errorDisplay.style.display = 'none';
        }
    }

    /**
     * Format a rank badge for top 3 positions
     * @param {number} rank - The rank number
     * @returns {string} HTML for rank display
     */
    function formatRank(rank) {
        if (rank <= 3) {
            return `<span class="rank-badge rank-${rank}">${rank}</span>`;
        }
        return rank.toString();
    }

    /**
     * Render a single scoreboard row
     * @param {Object} entry - Scoreboard entry data
     * @returns {string} HTML for the row
     */
    function renderRow(entry) {
        const isCurrentUser = state.currentUserId && state.currentUserId === entry.user_id;
        const highlightClass = isCurrentUser ? 'highlight' : '';

        return `
            <tr class="scoreboard-row ${highlightClass}" data-user-id="${entry.user_id}">
                <td class="col-rank">${formatRank(entry.rank)}</td>
                <td class="col-name">${escapeHtml(entry.display_name)}</td>
                <td class="col-score">${entry.total_score}</td>
                <td class="col-quizzes">${entry.quizzes_completed}</td>
            </tr>
        `;
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Update the scoreboard table with new data
     * @param {Array} entries - Array of scoreboard entries
     */
    function updateTable(entries) {
        if (!scoreboardBody) return;

        if (entries.length === 0) {
            scoreboardBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted" style="padding: 40px;">
                        No scores yet. Be the first to complete a quiz!
                    </td>
                </tr>
            `;
            return;
        }

        scoreboardBody.innerHTML = entries.map(renderRow).join('');
    }

    /**
     * Refresh scoreboard data via API
     */
    async function refreshScoreboard() {
        const currentPage = state.currentPage || 1;
        const url = `/api/scoreboard?page=${currentPage}&page_size=50`;

        showLoading();
        hideError();

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`Failed to load scoreboard: ${response.status}`);
            }

            const data = await response.json();
            updateTable(data.entries);

            // Update state
            state.currentUserId = data.current_user_id;

        } catch (error) {
            console.error('Error refreshing scoreboard:', error);
            showError('Failed to refresh scoreboard. Please try again.');
        } finally {
            hideLoading();
        }
    }

    /**
     * Navigate to a specific page
     * @param {number} page - Page number to navigate to
     */
    function navigateToPage(page) {
        window.location.href = `/scoreboard?page=${page}`;
    }

    /**
     * Jump to the current user's rank page
     */
    function jumpToMyRank() {
        if (jumpToRankBtn) {
            const targetPage = jumpToRankBtn.dataset.page;
            if (targetPage) {
                navigateToPage(parseInt(targetPage, 10));
            }
        }
    }

    /**
     * Initialize event listeners
     */
    function init() {
        // Refresh button
        if (refreshBtn) {
            refreshBtn.addEventListener('click', function(e) {
                e.preventDefault();
                refreshScoreboard();
            });
        }

        // Jump to rank button
        if (jumpToRankBtn) {
            jumpToRankBtn.addEventListener('click', function(e) {
                e.preventDefault();
                jumpToMyRank();
            });
        }

        // Pagination via JS (for dynamic navigation)
        document.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.dataset.page;
                if (page) {
                    navigateToPage(parseInt(page, 10));
                }
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
