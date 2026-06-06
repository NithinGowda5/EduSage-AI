document.addEventListener('DOMContentLoaded', () => {
    // State
    const state = {
        loggedIn: false,
        currentUser: null,
        cohereKeySet: false,
        openrouterKeySet: false,
        preferredProvider: 'cohere',
        openrouterModel: 'meta-llama/llama-3-8b-instruct:free',
        selectedFiles: [],
        ingestedDocuments: [],
        chatHistory: [],
        isSignUpMode: false,
        theme: 'dark' // default theme
    };

    // Elements
    const el = {
        // Auth
        loginScreen: document.getElementById('login-screen'),
        appShell: document.getElementById('app-shell'),
        loginForm: document.getElementById('login-form'),
        loginUsername: document.getElementById('login-username'),
        loginPassword: document.getElementById('login-password'),
        toggleSignup: document.getElementById('toggle-signup'),
        signupPromptBox: document.getElementById('signup-prompt-box'),
        formTitle: document.getElementById('form-title'),
        formSubtitle: document.getElementById('form-subtitle'),
        loginSubmitBtn: document.getElementById('login-submit-btn'),
        logoutBtn: document.getElementById('logout-btn'),
        userDisplayName: document.getElementById('user-display-name'),
        userAvatarInitial: document.getElementById('user-avatar-initial'),

        // Settings (Sidebar layout now)
        settingsToggle: document.getElementById('settings-toggle-btn'),
        settingsDrawer: document.getElementById('settings-drawer'),
        settingsOverlay: document.getElementById('settings-overlay'),
        settingsCloseBtn: document.getElementById('settings-close-btn'),
        providerSelect: document.getElementById('provider-select'),
        cohereConfigGroup: document.getElementById('cohere-config-group'),
        openrouterConfigGroup: document.getElementById('openrouter-config-group'),
        openrouterModelGroup: document.getElementById('openrouter-model-group'),
        cohereKeyInput: document.getElementById('cohere-key-input'),
        cohereStatusBadge: document.getElementById('cohere-status-badge'),
        saveCohereBtn: document.getElementById('save-cohere-btn'),
        openrouterKeyInput: document.getElementById('openrouter-key-input'),
        openrouterStatusBadge: document.getElementById('openrouter-status-badge'),
        saveOpenrouterBtn: document.getElementById('save-openrouter-btn'),
        openrouterModelSelect: document.getElementById('openrouter-model-select'),
        customModelInputGroup: document.getElementById('custom-model-input-group'),
        openrouterCustomModel: document.getElementById('openrouter-custom-model'),
        
        // Theme switcher
        themeToggleBtn: document.getElementById('theme-toggle-btn'),
        
        // Ingestion (on Home Page)
        dropzone: document.getElementById('dropzone'),
        fileInput: document.getElementById('file-uploader-input'),
        selectedFilesList: document.getElementById('selected-files-list'),
        processDocsBtn: document.getElementById('process-docs-btn'),
        documentsList: document.getElementById('documents-list'),
        
        // Hero
        heroInput: document.getElementById('chat-input-text-hero'),
        heroChatBtn: document.getElementById('hero-chat-btn'),
        heroReportBtn: document.getElementById('hero-report-btn'),
        heroAnalyticsBtn: document.getElementById('hero-analytics-btn'),
        
        // Results
        resultsSection: document.getElementById('results-section'),
        resultTypeBadge: document.getElementById('result-type-badge'),
        resultQueryText: document.getElementById('result-query-text'),
        resultContent: document.getElementById('result-content'),
        reportDownloadRow: document.getElementById('report-download-row'),
        downloadReportBtn: document.getElementById('download-report-btn'),
        
        // Analytics
        analyticsSection: document.getElementById('analytics-section'),
        refreshAnalyticsBtn: document.getElementById('refresh-analytics-btn'),
        metricTotalDocs: document.getElementById('metric-total-docs'),
        metricTotalChunks: document.getElementById('metric-total-chunks'),
        metricDbSize: document.getElementById('metric-db-size'),
        discoveredThemesList: document.getElementById('discovered-themes-list'),
        
        // History (in Settings Drawer now)
        historyContainer: document.getElementById('chat-history-container'),
        
        // Chat Panel (slide-in)
        chatFab: document.getElementById('chat-fab-btn'),
        chatPanel: document.getElementById('chat-panel'),
        chatPanelClose: document.getElementById('chat-panel-close'),
        chatMessagesBox: document.getElementById('chat-messages-box'),
        chatInputForm: document.getElementById('chat-input-form'),
        chatInputText: document.getElementById('chat-input-text'),
        chatSuggestions: document.getElementById('chat-suggestions'),
        toastContainer: document.getElementById('toast-container')
    };

    // ========== Theme Initialization & Switching ==========
    function initTheme() {
        const savedTheme = localStorage.getItem('edusage_theme') || 'dark';
        state.theme = savedTheme;
        if (savedTheme === 'light') {
            document.body.classList.add('theme-light');
        } else {
            document.body.classList.remove('theme-light');
        }
    }

    el.themeToggleBtn.addEventListener('click', () => {
        if (document.body.classList.contains('theme-light')) {
            document.body.classList.remove('theme-light');
            state.theme = 'dark';
            localStorage.setItem('edusage_theme', 'dark');
            showToast('Earthy Dark mode enabled', 'success');
        } else {
            document.body.classList.add('theme-light');
            state.theme = 'light';
            localStorage.setItem('edusage_theme', 'light');
            showToast('Earthy Light mode enabled', 'success');
        }
    });

    // ========== Authentication & Session Management ==========
    function checkAuth() {
        const sessionUser = localStorage.getItem('edusage_session_user');
        if (sessionUser) {
            state.loggedIn = true;
            state.currentUser = sessionUser;
            
            // Show app shell, hide login
            el.loginScreen.classList.add('hidden');
            el.appShell.classList.remove('hidden');
            
            // Update profile info
            el.userDisplayName.textContent = sessionUser;
            el.userAvatarInitial.textContent = sessionUser.charAt(0).toUpperCase();
            
            // Fetch initial RAG state
            checkConfig();
            fetchDocuments();
            refreshAnalytics();
        } else {
            state.loggedIn = false;
            state.currentUser = null;
            
            el.loginScreen.classList.remove('hidden');
            el.appShell.classList.add('hidden');
        }
    }

    // Toggle between Login and Signup modes
    el.toggleSignup.addEventListener('click', (e) => {
        e.preventDefault();
        state.isSignUpMode = !state.isSignUpMode;
        
        if (state.isSignUpMode) {
            el.formTitle.textContent = "Create account 🚀";
            el.formSubtitle.textContent = "Enter a username and password to sign up.";
            el.loginSubmitBtn.querySelector('span').textContent = "Sign Up &rarr;";
            el.signupPromptBox.innerHTML = 'Already have an account? <a href="#" id="toggle-login-back">Log in</a>';
            
            document.getElementById('toggle-login-back').addEventListener('click', (ev) => {
                ev.preventDefault();
                el.toggleSignup.click();
            });
        } else {
            el.formTitle.textContent = "Welcome back 👋";
            el.formSubtitle.textContent = "Please log in to access this page.";
            el.loginSubmitBtn.querySelector('span').textContent = "Login &rarr;";
            el.signupPromptBox.innerHTML = 'New to EduSage AI? <a href="#" id="toggle-signup">Create a free account</a>';
            
            // Re-bind the signup toggle element
            const newToggle = document.getElementById('toggle-signup');
            newToggle.addEventListener('click', (ev) => {
                ev.preventDefault();
                el.toggleSignup.click();
            });
        }
    });

    // Handle Login Form submission
    el.loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = el.loginUsername.value.trim();
        const password = el.loginPassword.value;

        if (!username || !password) {
            showToast('Please enter both username and password', 'error');
            return;
        }

        if (state.isSignUpMode) {
            // Mock signup
            const users = JSON.parse(localStorage.getItem('edusage_mock_users') || '{}');
            if (users[username]) {
                showToast('Username already exists. Please choose another.', 'error');
                return;
            }
            users[username] = password;
            localStorage.setItem('edusage_mock_users', JSON.stringify(users));
            showToast('Account created successfully! Please log in.', 'success');
            
            // Switch back to Login mode
            state.isSignUpMode = false;
            el.loginUsername.value = username;
            el.loginPassword.value = '';
            el.toggleSignup.click();
        } else {
            // Mock login
            const users = JSON.parse(localStorage.getItem('edusage_mock_users') || '{"admin":"admin"}');
            
            if (users[username] && users[username] === password) {
                localStorage.setItem('edusage_session_user', username);
                showToast(`Welcome back, ${username}!`, 'success');
                checkAuth();
            } else if (username === 'admin' && password === 'admin') {
                localStorage.setItem('edusage_session_user', username);
                showToast(`Welcome back, ${username}!`, 'success');
                checkAuth();
            } else {
                // Auto-register for easy prototyping
                users[username] = password;
                localStorage.setItem('edusage_mock_users', JSON.stringify(users));
                localStorage.setItem('edusage_session_user', username);
                showToast(`Created new profile and logged in as ${username}!`, 'success');
                checkAuth();
            }
        }
    });

    // Handle Logout
    el.logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('edusage_session_user');
        showToast('Logged out successfully', 'info');
        checkAuth();
        // Close sidebar upon logout
        closeSettings();
    });

    // ========== Settings Sidebar (Open/Close logic with overlay) ==========
    function openSettings() {
        el.settingsDrawer.classList.remove('hidden');
        el.settingsOverlay.classList.remove('hidden');
        el.settingsToggle.classList.add('active');
        document.body.style.overflow = 'hidden'; // prevent main content scrolling
    }

    function closeSettings() {
        el.settingsDrawer.classList.add('hidden');
        el.settingsOverlay.classList.add('hidden');
        el.settingsToggle.classList.remove('active');
        document.body.style.overflow = ''; // restore scrolling
    }

    el.settingsToggle.addEventListener('click', () => {
        const isOpen = !el.settingsDrawer.classList.contains('hidden');
        if (isOpen) {
            closeSettings();
        } else {
            openSettings();
        }
    });

    el.settingsCloseBtn.addEventListener('click', closeSettings);
    el.settingsOverlay.addEventListener('click', closeSettings);

    // ========== Chat FAB ==========
    el.chatFab.addEventListener('click', () => {
        el.chatPanel.classList.toggle('hidden');
    });
    el.chatPanelClose.addEventListener('click', () => {
        el.chatPanel.classList.add('hidden');
    });

    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            el.chatInputText.value = chip.dataset.query;
            el.chatInputText.focus();
        });
    });

    // ========== Toast ==========
    function showToast(msg, type = 'info') {
        const t = document.createElement('div');
        t.className = `toast toast-${type}`;
        const s = document.createElement('span');
        s.textContent = msg;
        t.appendChild(s);
        const c = document.createElement('button');
        c.className = 'toast-close';
        c.innerHTML = '&times;';
        c.onclick = () => t.remove();
        t.appendChild(c);
        el.toastContainer.appendChild(t);
        setTimeout(() => { 
            if (t.parentNode) { 
                t.style.opacity = '0'; 
                t.style.transform = 'translateY(10px)'; 
                t.style.transition = 'all 0.25s ease'; 
                setTimeout(() => t.remove(), 250); 
            } 
        }, 4000);
    }

    // ========== Markdown ==========
    function parseMarkdown(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
            .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
            .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>')
            .replace(/(<li>.*?<\/li>)/g, '<ul>$1</ul>')
            .replace(/<\/ul>\s*<ul>/g, '')
            .replace(/^(?!(?:<h|<li|<ul))(.*?)$/gm, (m) => m.trim() ? `<p>${m}</p>` : '');
    }

    // ========== Config ==========
    async function checkConfig() {
        try {
            const res = await fetch('/api/config');
            if (res.ok) {
                const d = await res.json();
                state.cohereKeySet = d.cohere_key_set;
                state.openrouterKeySet = d.openrouter_key_set;
                state.preferredProvider = d.preferred_provider || 'cohere';
                state.openrouterModel = d.openrouter_model || 'meta-llama/llama-3-8b-instruct:free';
                updateConfigUI();
            }
        } catch(e) { console.error(e); }
    }

    function updateConfigUI() {
        el.providerSelect.value = state.preferredProvider;
        if (state.preferredProvider === 'cohere') {
            el.cohereConfigGroup.classList.remove('hidden');
            el.openrouterConfigGroup.classList.add('hidden');
            el.openrouterModelGroup.classList.add('hidden');
        } else {
            el.cohereConfigGroup.classList.add('hidden');
            el.openrouterConfigGroup.classList.remove('hidden');
            el.openrouterModelGroup.classList.remove('hidden');
        }
        setBadge(el.cohereStatusBadge, state.cohereKeySet);
        el.cohereKeyInput.placeholder = state.cohereKeySet ? '••••••••••' : 'sk-...';
        setBadge(el.openrouterStatusBadge, state.openrouterKeySet);
        el.openrouterKeyInput.placeholder = state.openrouterKeySet ? '••••••••••' : 'sk-or-...';
        const known = ['meta-llama/llama-3-8b-instruct:free','mistralai/mistral-7b-instruct:free','google/gemma-2-9b-it:free','openchat/openchat-7b:free','anthropic/claude-3.5-sonnet','google/gemini-pro','meta-llama/llama-3-70b-instruct'];
        if (known.includes(state.openrouterModel)) {
            el.openrouterModelSelect.value = state.openrouterModel;
            el.customModelInputGroup.classList.add('hidden');
        } else {
            el.openrouterModelSelect.value = 'custom';
            el.openrouterCustomModel.value = state.openrouterModel;
            el.customModelInputGroup.classList.remove('hidden');
        }
    }

    function setBadge(b, s) { b.className = s ? 'badge badge-success' : 'badge badge-error'; b.textContent = s ? 'Active' : 'Not Set'; }

    el.providerSelect.addEventListener('change', async () => {
        state.preferredProvider = el.providerSelect.value;
        updateConfigUI();
        try { 
            await fetch('/api/config', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ preferred_provider: state.preferredProvider }) 
            }); 
            showToast(`Provider: ${state.preferredProvider}`, 'success'); 
        } catch(e) {}
    });

    el.openrouterModelSelect.addEventListener('change', async () => {
        const v = el.openrouterModelSelect.value;
        if (v === 'custom') { el.customModelInputGroup.classList.remove('hidden'); return; }
        el.customModelInputGroup.classList.add('hidden');
        state.openrouterModel = v;
        try { 
            await fetch('/api/config', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ openrouter_model: v }) 
            }); 
            showToast(`Model: ${v}`, 'success'); 
        } catch(e) {}
    });

    el.openrouterCustomModel.addEventListener('blur', async () => {
        const v = el.openrouterCustomModel.value.trim();
        if (!v) return;
        state.openrouterModel = v;
        try { 
            await fetch('/api/config', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ openrouter_model: v }) 
            }); 
            showToast(`Model: ${v}`, 'success'); 
        } catch(e) {}
    });

    async function saveKey(type, input, stateKey) {
        const key = input.value.trim();
        if (!key) { showToast('Enter an API key first', 'error'); return; }
        const body = {}; body[type] = key;
        try {
            const res = await fetch('/api/config', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(body) 
            });
            if (res.ok) { 
                state[stateKey] = true; 
                input.value = ''; 
                updateConfigUI(); 
                showToast('API key saved', 'success'); 
                checkConfig(); 
            }
            else showToast('Failed to save key', 'error');
        } catch(e) { showToast('Error saving key', 'error'); }
    }

    el.saveCohereBtn.addEventListener('click', () => saveKey('cohere_api_key', el.cohereKeyInput, 'cohereKeySet'));
    el.saveOpenrouterBtn.addEventListener('click', () => saveKey('openrouter_api_key', el.openrouterKeyInput, 'openrouterKeySet'));

    // ========== Files ==========
    el.dropzone.addEventListener('click', () => el.fileInput.click());
    el.dropzone.addEventListener('dragover', e => { e.preventDefault(); el.dropzone.classList.add('dragover'); });
    ['dragleave','dragend'].forEach(ev => el.dropzone.addEventListener(ev, () => el.dropzone.classList.remove('dragover')));
    el.dropzone.addEventListener('drop', e => { e.preventDefault(); el.dropzone.classList.remove('dragover'); if(e.dataTransfer.files.length) handleFiles(e.dataTransfer.files); });
    el.fileInput.addEventListener('change', () => { if(el.fileInput.files.length) handleFiles(el.fileInput.files); });

    function handleFiles(files) {
        for (const f of files) {
            if (f.type !== 'application/pdf') { showToast(`${f.name} is not PDF`, 'error'); continue; }
            if (!state.selectedFiles.some(x => x.name === f.name)) state.selectedFiles.push(f);
        }
        renderSelected();
    }

    function renderSelected() {
        el.selectedFilesList.innerHTML = '';
        state.selectedFiles.forEach((f, i) => {
            const d = document.createElement('div'); d.className = 'selected-file-item';
            const s = document.createElement('span'); s.textContent = f.name; d.appendChild(s);
            const r = document.createElement('button'); r.innerHTML = '&times;'; r.onclick = () => { state.selectedFiles.splice(i, 1); renderSelected(); }; d.appendChild(r);
            el.selectedFilesList.appendChild(d);
        });
        el.processDocsBtn.disabled = state.selectedFiles.length === 0;
    }

    el.processDocsBtn.addEventListener('click', async () => {
        if (!state.cohereKeySet) { showToast('Set Cohere API Key in Settings first', 'error'); return; }
        const form = new FormData();
        state.selectedFiles.forEach(f => form.append('files', f));
        const bt = el.processDocsBtn.querySelector('.btn-text');
        const bl = el.processDocsBtn.querySelector('.btn-loader');
        bt.textContent = 'Processing...'; bl.classList.remove('hidden'); el.processDocsBtn.disabled = true;
        try {
            const res = await fetch('/api/documents/upload', { method: 'POST', body: form });
            if (res.ok) { 
                const d = await res.json(); 
                showToast(d.message, 'success'); 
                state.selectedFiles = []; 
                renderSelected(); 
                fetchDocuments(); 
                refreshAnalytics(); 
            }
            else { 
                const e = await res.json(); 
                showToast(e.detail || 'Failed to process document', 'error'); 
            }
        } catch(e) { showToast('Upload error', 'error'); }
        finally { bt.textContent = 'Process Documents'; bl.classList.add('hidden'); renderSelected(); }
    });

    async function fetchDocuments() {
        try { 
            const res = await fetch('/api/documents'); 
            if (res.ok) { 
                state.ingestedDocuments = await res.json(); 
                renderDocs(); 
            } 
        } catch(e) {}
    }

    function renderDocs() {
        el.documentsList.innerHTML = '';
        if (!state.ingestedDocuments.length) {
            const li = document.createElement('li'); 
            li.className = 'empty-list-msg'; 
            li.textContent = 'No documents processed yet.'; 
            el.documentsList.appendChild(li); 
            return;
        }
        state.ingestedDocuments.forEach(name => {
            const li = document.createElement('li');
            const sp = document.createElement('span'); 
            sp.className = 'doc-name'; 
            sp.textContent = name; 
            li.appendChild(sp);
            const dl = document.createElement('button'); 
            dl.className = 'del-doc-btn'; 
            dl.innerHTML = '&times;'; 
            dl.onclick = () => deleteDoc(name); 
            li.appendChild(dl);
            el.documentsList.appendChild(li);
        });
    }

    async function deleteDoc(name) {
        if (!confirm(`Delete ${name}?`)) return;
        try { 
            const res = await fetch(`/api/documents/${encodeURIComponent(name)}`, { method: 'DELETE' }); 
            if (res.ok) { 
                showToast(`Deleted ${name}`, 'success'); 
                fetchDocuments(); 
                refreshAnalytics(); 
            } else {
                showToast('Delete failed', 'error'); 
            }
        } catch(e) { showToast('Error deleting document', 'error'); }
    }

    // ========== Hero Actions ==========
    el.heroChatBtn.addEventListener('click', async () => {
        const query = el.heroInput.value.trim();
        if (!query) { showToast('Enter a question first', 'error'); return; }
        el.heroChatBtn.querySelector('span').textContent = '⏳ Thinking...';
        el.heroChatBtn.disabled = true;
        el.analyticsSection.classList.add('hidden');
        el.reportDownloadRow.classList.add('hidden');
        try {
            const res = await fetch('/api/chat', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ message: query }) 
            });
            if (res.ok) {
                const d = await res.json();
                showResult('CHAT RESPONSE', query, d.answer, d.citations);
                addToHistory('Chat', query);
            } else { 
                const e = await res.json(); 
                showResult('ERROR', query, e.detail || 'Could not get response.'); 
            }
        } catch(e) { showResult('ERROR', query, 'Network error.'); }
        finally { el.heroChatBtn.querySelector('span').textContent = '💬 Ask Question'; el.heroChatBtn.disabled = false; }
    });

    el.heroReportBtn.addEventListener('click', async () => {
        const query = el.heroInput.value.trim();
        if (!query) { showToast('Enter a research topic', 'error'); return; }
        el.heroReportBtn.querySelector('span').textContent = '⏳ Generating...';
        el.heroReportBtn.disabled = true;
        el.analyticsSection.classList.add('hidden');
        el.reportDownloadRow.classList.add('hidden');
        try {
            const res = await fetch('/api/report', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ query }) 
            });
            if (res.ok) {
                const d = await res.json();
                showResult('RESEARCH REPORT', query, d.report);
                el.downloadReportBtn.href = `/api/report/download?filename=${encodeURIComponent(d.filename)}`;
                el.reportDownloadRow.classList.remove('hidden');
                addToHistory('Report', query);
            } else { 
                const e = await res.json(); 
                showResult('ERROR', query, e.detail || 'Report failed.'); 
            }
        } catch(e) { showResult('ERROR', query, 'Network error.'); }
        finally { el.heroReportBtn.querySelector('span').textContent = '📊 Generate Report'; el.heroReportBtn.disabled = false; }
    });

    el.heroAnalyticsBtn.addEventListener('click', () => {
        el.resultsSection.classList.add('hidden');
        el.reportDownloadRow.classList.add('hidden');
        el.analyticsSection.classList.remove('hidden');
        refreshAnalytics();
        el.analyticsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    function showResult(type, query, content, citations) {
        el.resultTypeBadge.textContent = type;
        el.resultTypeBadge.className = type === 'ERROR' ? 'result-type-badge' : 'result-type-badge';
        el.resultQueryText.textContent = `"${query}"`;

        let html = parseMarkdown(content);
        if (citations && citations.length) {
            html += '<div class="citations-expander"><button class="citations-trigger" onclick="this.nextElementSibling.classList.toggle(\'expanded\');this.innerHTML=this.nextElementSibling.classList.contains(\'expanded\')?\'Sources (' + citations.length + ') ▴\':\'Sources (' + citations.length + ') ▾\'">Sources (' + citations.length + ') ▾</button><div class="citations-content">';
            citations.forEach((c, i) => { html += `<div class="citation-item"><strong>${i+1}. ${c.source} (p. ${c.page})</strong><br><em>"${c.text}"</em></div>`; });
            html += '</div></div>';
        }

        el.resultContent.innerHTML = html;
        el.resultsSection.classList.remove('hidden');
        el.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // ========== History ==========
    function addToHistory(type, query) {
        state.chatHistory.unshift({ type, query, time: new Date().toLocaleTimeString() });
        renderHistory();
    }

    function renderHistory() {
        el.historyContainer.innerHTML = '';
        if (!state.chatHistory.length) {
            el.historyContainer.innerHTML = '<p class="empty-history">No history yet. Start by asking a question above!</p>';
            return;
        }
        state.chatHistory.forEach((item, idx) => {
            const div = document.createElement('div'); div.className = 'history-item';
            const info = document.createElement('div'); info.className = 'history-item-info';
            const q = document.createElement('div'); q.className = 'history-item-query'; q.textContent = item.query; info.appendChild(q);
            const m = document.createElement('div'); m.className = 'history-item-meta'; m.textContent = `${item.type} • ${item.time}`; info.appendChild(m);
            div.appendChild(info);
            const btn = document.createElement('button'); btn.className = 'history-view-btn'; btn.textContent = 'View';
            btn.addEventListener('click', () => {
                el.heroInput.value = item.query;
                // Close sidebar to let user see
                closeSettings();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            div.appendChild(btn);
            el.historyContainer.appendChild(div);
        });
    }

    // ========== Chat Panel ==========
    el.chatInputForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = el.chatInputText.value.trim();
        if (!msg) return;
        el.chatInputText.value = '';
        el.chatSuggestions.classList.add('hidden');
        appendChatMsg('user', msg);
        const lid = appendChatLoader();
        try {
            const res = await fetch('/api/chat', { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify({ message: msg }) 
            });
            removeChatLoader(lid);
            if (res.ok) { 
                const d = await res.json(); 
                appendChatMsg('assistant', d.answer); 
            }
            else { 
                const e = await res.json(); 
                appendChatMsg('assistant', `Error: ${e.detail || 'Failed'}`); 
            }
        } catch(err) { 
            removeChatLoader(lid); 
            appendChatMsg('assistant', 'Error: Network failure.'); 
        }
    });

    function appendChatMsg(role, content) {
        const m = document.createElement('div');
        m.className = `message ${role}-message`;
        const c = document.createElement('div');
        c.className = 'message-content';
        c.innerHTML = role === 'user' ? `<p>${content}</p>` : parseMarkdown(content);
        m.appendChild(c);
        el.chatMessagesBox.appendChild(m);
        el.chatMessagesBox.scrollTop = el.chatMessagesBox.scrollHeight;
    }

    function appendChatLoader() {
        const id = 'cl_' + Date.now();
        const m = document.createElement('div'); m.className = 'message assistant-message'; m.id = id;
        const c = document.createElement('div'); c.className = 'message-content';
        c.innerHTML = '<div class="message-loader"><span></span><span></span><span></span></div>';
        m.appendChild(c);
        el.chatMessagesBox.appendChild(m);
        el.chatMessagesBox.scrollTop = el.chatMessagesBox.scrollHeight;
        return id;
    }

    function removeChatLoader(id) { const e = document.getElementById(id); if (e) e.remove(); }

    // ========== Analytics ==========
    el.refreshAnalyticsBtn.addEventListener('click', refreshAnalytics);

    async function refreshAnalytics() {
        try {
            const res = await fetch('/api/analytics');
            if (res.ok) {
                const d = await res.json();
                el.metricTotalDocs.textContent = d.total_docs;
                el.metricTotalChunks.textContent = d.total_chunks;
                el.metricDbSize.textContent = d.db_size;
                el.discoveredThemesList.innerHTML = '';
                if (d.themes && d.themes.length) {
                    d.themes.forEach(t => { const li = document.createElement('li'); li.textContent = t; el.discoveredThemesList.appendChild(li); });
                } else {
                    const li = document.createElement('li'); li.textContent = 'No themes discovered yet.'; el.discoveredThemesList.appendChild(li);
                }
            }
        } catch(e) { console.error(e); }
    }

    // ========== Views Navigation Switcher (Rolling Slide) ==========
    const navLinks = document.querySelectorAll('.nav-link, .footer-link-item');
    const appViews = document.querySelectorAll('.app-view');
    const viewOrder = ['home-view', 'manifesto-view', 'plans-view', 'connect-view'];
    let currentViewIndex = 0;

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            if (!targetId) return;

            const targetIndex = viewOrder.indexOf(targetId);
            if (targetIndex === -1 || targetIndex === currentViewIndex) return;

            // Determine slide direction
            const slideDirection = targetIndex > currentViewIndex ? 'slide-left' : 'slide-right';
            currentViewIndex = targetIndex;

            // Switch active link class across all selectors
            navLinks.forEach(l => {
                if (l.getAttribute('data-target') === targetId) {
                    l.classList.add('active');
                } else {
                    l.classList.remove('active');
                }
            });

            // Switch visible view with direction-based animation
            appViews.forEach(view => {
                if (view.id === targetId) {
                    view.classList.remove('hidden', 'slide-left', 'slide-right');
                    // Force reflow to restart animation
                    void view.offsetWidth;
                    view.classList.add(slideDirection);
                } else {
                    view.classList.add('hidden');
                    view.classList.remove('slide-left', 'slide-right');
                }
            });

            // Close settings if open
            closeSettings();
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // ========== Click to Copy ==========
    const copyableCards = document.querySelectorAll('.channel-card.copyable');
    copyableCards.forEach(card => {
        card.addEventListener('click', async () => {
            const textToCopy = card.getAttribute('data-copy');
            if (!textToCopy) return;

            const label = card.querySelector('.channel-label').textContent.toLowerCase();
            const hint = card.querySelector('.copy-hint');

            const triggerFeedback = () => {
                showToast(`Copied ${label} to clipboard!`, 'success');
                if (hint) {
                    const originalText = hint.textContent;
                    hint.textContent = 'Copied!';
                    hint.style.background = 'var(--success-bg)';
                    hint.style.color = 'var(--success)';
                    setTimeout(() => {
                        hint.textContent = originalText;
                        hint.style.background = '';
                        hint.style.color = '';
                    }, 2000);
                }
            };

            if (navigator.clipboard && navigator.clipboard.writeText) {
                try {
                    await navigator.clipboard.writeText(textToCopy);
                    triggerFeedback();
                    return;
                } catch (err) {
                    console.warn('Clipboard API failed, trying fallback...', err);
                }
            }

            // Fallback selection and execCommand
            const textarea = document.createElement('textarea');
            textarea.value = textToCopy;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                triggerFeedback();
            } catch (err) {
                showToast('Failed to copy to clipboard', 'error');
                console.error('Copy fallback failed:', err);
            }
            document.body.removeChild(textarea);
        });
    });

    // Init theme and check authentication
    initTheme();
    checkAuth();
});
