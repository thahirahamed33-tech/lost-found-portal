/* ========================================
   CampusLost - College Lost & Found Portal
   JavaScript Application (Flask Version)
   ======================================== */

// API Base URL - Flask backend routes
const API_URL = '';

// ========================================
// State Management
// ========================================

let currentUser = null;
let currentPage = 'home';
let reportType = 'lost';
let uploadedImage = null;
let authToken = null;

// Get current page from URL
function getCurrentPage() {
    const path = window.location.pathname;
    if (path === '/' || path === '') return 'home';
    if (path === '/lost') return 'lost';
    if (path === '/found') return 'found';
    if (path === '/myitems') return 'myitems';
    if (path === '/report') return 'report';
    if (path === '/dashboard') return 'dashboard';
    if (path === '/admin') return 'admin';
    return 'home';
}

// Initialize app
function init() {
    loadUserFromStorage();
    setupEventListeners();
    updateUI();
    
    // Load data based on current page
    const page = getCurrentPage();
    navigateToPage(page);
}

function navigateToPage(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // Show selected page
    const pageElement = document.getElementById(page + 'Page');
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        const linkPage = link.getAttribute('data-page');
        if (linkPage === page) {
            link.classList.add('active');
        }
    });
    
    currentPage = page;
    
    // Load page data
    switch (page) {
        case 'home':
            loadStats();
            loadRecentItems();
            break;
        case 'lost':
            loadLostItems();
            break;
        case 'found':
            loadFoundItems();
            break;
        case 'myitems':
            if (!currentUser) {
                showToast('error', 'Login Required', 'Please login to view your items');
                openAuthModal();
                return;
            }
            loadMyItems();
            break;
        case 'report':
            if (!currentUser) {
                showToast('error', 'Login Required', 'Please login to report an item');
                openAuthModal();
                return;
            }
            resetReportForm();
            break;
        case 'dashboard':
            if (!currentUser) {
                showToast('error', 'Login Required', 'Please login to view dashboard');
                openAuthModal();
                return;
            }
            loadDashboard();
            break;
        case 'admin':
            if (!currentUser || currentUser.role !== 'admin') {
                showToast('error', 'Access Denied', 'Admin access required');
                window.location.href = '/';
                return;
            }
            loadAdminDashboard();
            break;
    }
}

// ========================================
// User Authentication
// ========================================

function loadUserFromStorage() {
    const user = localStorage.getItem('campusLost_user');
    const token = localStorage.getItem('campusLost_token');
    
    if (user && user !== 'null') {
        currentUser = JSON.parse(user);
        authToken = token;
    }
}

function saveUser(user, token) {
    currentUser = user;
    authToken = token;
    localStorage.setItem('campusLost_user', JSON.stringify(user));
    localStorage.setItem('campusLost_token', token);
}

function logout() {
    currentUser = null;
    authToken = null;
    localStorage.removeItem('campusLost_user');
    localStorage.removeItem('campusLost_token');
    updateUI();
    navigateTo('/');
    showToast('info', 'Logged Out', 'You have been logged out');
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            saveUser(data.user, data.token);
            closeAuthModal();
            updateUI();
            showToast('success', 'Welcome back!', `Logged in as ${data.user.name}`);
            navigateTo('/');
        } else {
            showToast('error', 'Login Failed', data.error);
        }
    } catch (error) {
        showToast('error', 'Login Failed', 'Network error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    
    if (password !== confirmPassword) {
        showToast('error', 'Registration Failed', 'Passwords do not match');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            saveUser(data.user, data.token);
            closeAuthModal();
            updateUI();
            showToast('success', 'Welcome!', 'Account created successfully');
            navigateTo('/');
        } else {
            showToast('error', 'Registration Failed', data.error);
        }
    } catch (error) {
        showToast('error', 'Registration Failed', 'Network error');
    }
}

// ========================================
// UI Components
// ========================================

function updateUI() {
    const userSection = document.getElementById('userSection');
    const userDropdown = document.getElementById('userDropdown');
    const adminLink = document.getElementById('adminLink');
    
    if (currentUser) {
        userSection.classList.add('hidden');
        userDropdown.classList.remove('hidden');
        
        document.getElementById('userAvatar').textContent = currentUser.name.charAt(0).toUpperCase();
        document.getElementById('userName').textContent = currentUser.name;
        document.getElementById('userEmail').textContent = currentUser.email;
        
        if (currentUser.role === 'admin') {
            adminLink.style.display = 'flex';
        } else {
            adminLink.style.display = 'none';
        }
    } else {
        userSection.classList.remove('hidden');
        userDropdown.classList.add('hidden');
    }
    
    updateNotificationBadge();
}

function toggleMobileMenu() {
    const nav = document.getElementById('mainNav');
    nav.classList.toggle('show');
}

function toggleUserMenu() {
    const menu = document.getElementById('dropdownMenu');
    menu.classList.toggle('show');
}

function toggleNotifications() {
    const panel = document.getElementById('notificationPanel');
    panel.classList.toggle('hidden');
    loadNotifications();
}

// ========================================
// Auth Modal
// ========================================

function openAuthModal(tab = 'login') {
    const modal = document.getElementById('authModal');
    modal.classList.remove('hidden');
    switchAuthTab(tab);
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.add('hidden');
    document.getElementById('loginForm').reset();
    document.getElementById('registerForm').reset();
}

function switchAuthTab(tab) {
    const tabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    tabs.forEach(t => {
        t.classList.remove('active');
        if (t.dataset.tab === tab) {
            t.classList.add('active');
        }
    });
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    }
}

// ========================================
// Data Loading
// ========================================

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/api/items`);
        const items = await response.json();
        
        const lostItems = items.filter(i => i.type === 'lost').length;
        const foundItems = items.filter(i => i.type === 'found').length;
        const resolved = items.filter(i => i.status === 'resolved' || i.status === 'claimed').length;
        
        document.getElementById('totalLostItems').textContent = lostItems;
        document.getElementById('totalFoundItems').textContent = foundItems;
        document.getElementById('totalReunited').textContent = resolved;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadRecentItems() {
    try {
        const response = await fetch(`${API_URL}/api/items`);
        const items = await response.json();
        const recentItems = items.slice(0, 6);
        
        const grid = document.getElementById('recentItemsGrid');
        grid.innerHTML = recentItems.map(item => createItemCard(item)).join('');
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

// ========================================
// Helper Functions
// ========================================

function createItemCard(item) {
    const icon = getCategoryIcon(item.category);
    const typeLabel = item.type === 'lost' ? 'Lost' : 'Found';
    const statusClass = item.status === 'resolved' || item.status === 'claimed' ? 'resolved' : item.status;
    
    return `
        <div class="item-card">
            <div class="item-image">${icon}</div>
            <div class="item-body">
                <div class="item-header">
                    <h3 class="item-name">${item.name}</h3>
                    <span class="item-badge ${item.type}">${typeLabel}</span>
                </div>
                <span class="item-category">${capitalize(item.category)}</span>
                <div class="item-details">
                    <div class="item-detail">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        ${item.location}
                    </div>
                    <div class="item-detail">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        ${formatDate(item.date)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getCategoryIcon(category) {
    const icons = {
        electronics: '💻',
        books: '📚',
        clothing: '👕',
        accessories: '⌚',
        wallet: '👝',
        other: '📦'
    };
    return icons[category] || '📦';
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(date) {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function navigateTo(page) {
    window.location.href = page;
}

function filterByCategory(category) {
    window.location.href = `/lost?category=${category}`;
}

function switchRecentTab(tab) {
    const tabs = document.querySelectorAll('.section-tabs .tab-btn');
    tabs.forEach(t => {
        t.classList.remove('active');
        if (t.dataset.tab === tab) {
            t.classList.add('active');
        }
    });
    
    const typeParam = tab === 'recent' ? '' : `?type=${tab}`;
    fetch(`${API_URL}/api/items${typeParam}`)
        .then(res => res.json())
        .then(items => {
            const grid = document.getElementById('recentItemsGrid');
            grid.innerHTML = items.slice(0, 6).map(item => createItemCard(item)).join('');
        });
}

// ========================================
// Lost Items Page
// ========================================

async function loadLostItems() {
    try {
        const search = document.getElementById('lostSearchInput')?.value || '';
        const category = document.getElementById('lostCategoryFilter')?.value || '';
        
        let url = `${API_URL}/api/items?type=lost`;
        if (category) url += `&category=${category}`;
        if (search) url += `&search=${search}`;
        
        const response = await fetch(url);
        const items = await response.json();
        
        const grid = document.getElementById('lostItemsGrid');
        if (items.length === 0) {
            grid.innerHTML = '<div class="empty-state">No lost items found</div>';
        } else {
            grid.innerHTML = items.map(item => createItemCard(item)).join('');
        }
    } catch (error) {
        console.error('Error loading lost items:', error);
    }
}

function filterItems(type) {
    if (type === 'lost') {
        loadLostItems();
    } else if (type === 'found') {
        loadFoundItems();
    }
}

// ========================================
// Found Items Page
// ========================================

async function loadFoundItems() {
    try {
        const search = document.getElementById('foundSearchInput')?.value || '';
        const category = document.getElementById('foundCategoryFilter')?.value || '';
        
        let url = `${API_URL}/api/items?type=found`;
        if (category) url += `&category=${category}`;
        if (search) url += `&search=${search}`;
        
        const response = await fetch(url);
        const items = await response.json();
        
        const grid = document.getElementById('foundItemsGrid');
        if (items.length === 0) {
            grid.innerHTML = '<div class="empty-state">No found items found</div>';
        } else {
            grid.innerHTML = items.map(item => createItemCard(item)).join('');
        }
    } catch (error) {
        console.error('Error loading found items:', error);
    }
}

// ========================================
// My Items Page
// ========================================

async function loadMyItems() {
    switchMyItemsTab('lost');
}

function switchMyItemsTab(tab) {
    const tabs = document.querySelectorAll('#myitemsPage .myitems-tabs .tab-btn');
    tabs.forEach(t => {
        t.classList.remove('active');
        if (t.textContent.toLowerCase().includes(tab === 'lost' ? 'lost' : tab === 'found' ? 'found' : 'claims')) {
            t.classList.add('active');
        }
    });
    
    const content = document.getElementById('myitemsContent');
    
    if (tab === 'lost' || tab === 'found') {
        fetch(`${API_URL}/api/my-items?type=${tab}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(res => res.json())
        .then(items => {
            if (items.length === 0) {
                content.innerHTML = '<div class="empty-state">No items found</div>';
            } else {
                content.innerHTML = `<div class="items-grid">${items.map(item => createItemCard(item)).join('')}</div>`;
            }
        });
    } else if (tab === 'claims') {
        fetch(`${API_URL}/api/my-claims`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(res => res.json())
        .then(claims => {
            if (claims.length === 0) {
                content.innerHTML = '<div class="empty-state">No claims found</div>';
            } else {
                content.innerHTML = `
                    <div class="admin-table">
                        <table>
                            <thead>
                                <tr><th>Item</th><th>Date</th><th>Status</th></tr>
                            </thead>
                            <tbody>
                                ${claims.map(claim => `
                                    <tr>
                                        <td>${claim.item_name}</td>
                                        <td>${formatDate(claim.created_at)}</td>
                                        <td><span class="status-badge ${claim.status}">${capitalize(claim.status)}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }
        });
    }
}

// ========================================
// Report Item
// ========================================

function selectReportType(type) {
    reportType = type;
    const buttons = document.querySelectorAll('.type-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.type === type) {
            btn.classList.add('active');
        }
    });
}

function resetReportForm() {
    document.getElementById('reportForm').reset();
    document.getElementById('itemDate').valueAsDate = new Date();
    document.getElementById('otherLocationGroup').style.display = 'none';
}

function toggleOtherLocation() {
    const locationSelect = document.getElementById('itemLocation');
    const otherGroup = document.getElementById('otherLocationGroup');
    const otherInput = document.getElementById('otherLocation');
    
    if (locationSelect.value === 'Other') {
        otherGroup.style.display = 'block';
        otherInput.setAttribute('required', 'true');
    } else {
        otherGroup.style.display = 'none';
        otherInput.removeAttribute('required');
        otherInput.value = '';
    }
}

async function submitReport(event) {
    event.preventDefault();
    
    if (!authToken) {
        showToast('error', 'Login Required', 'Please login to report an item');
        openAuthModal();
        return;
    }
    
    const name = document.getElementById('itemName').value;
    const category = document.getElementById('itemCategory').value;
    const description = document.getElementById('itemDescription').value;
    let location = document.getElementById('itemLocation').value;
    const date = document.getElementById('itemDate').value;
    
    // Handle "Other" location
    if (location === 'Other') {
        location = document.getElementById('otherLocation').value;
        if (!location) {
            showToast('error', 'Required', 'Please specify the location');
            return;
        }
    }
    
    try {
        const response = await fetch(`${API_URL}/api/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                type: reportType,
                name,
                category,
                description,
                location,
                date
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('success', 'Item Reported', `Your ${reportType} item has been posted`);
            navigateTo(reportType === 'lost' ? '/lost' : '/found');
        } else {
            showToast('error', 'Error', data.error);
        }
    } catch (error) {
        showToast('error', 'Error', 'Failed to submit report');
    }
}

// ========================================
// Dashboard
// ========================================

async function loadDashboard() {
    document.getElementById('dashboardUserName').textContent = currentUser.name;
    
    try {
        const response = await fetch(`${API_URL}/api/my-items`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const items = await response.json();
        
        const myLost = items.filter(i => i.type === 'lost').length;
        const myFound = items.filter(i => i.type === 'found').length;
        const resolved = items.filter(i => i.status === 'resolved' || i.status === 'claimed').length;
        
        document.getElementById('myLostCount').textContent = myLost;
        document.getElementById('myFoundCount').textContent = myFound;
        document.getElementById('myResolvedCount').textContent = resolved;
        
        // Claims
        const claimsRes = await fetch(`${API_URL}/api/my-claims`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const claims = await claimsRes.json();
        const pending = claims.filter(c => c.status === 'pending').length;
        document.getElementById('myClaimsCount').textContent = pending;
        
        // Recent activity
        const activityList = document.getElementById('activityList');
        if (items.length === 0) {
            activityList.innerHTML = '<div class="empty-state">No recent activity</div>';
        } else {
            activityList.innerHTML = items.slice(0, 5).map(item => `
                <div class="activity-item">
                    <div class="activity-icon">${item.type === 'lost' ? '🔍' : '✨'}</div>
                    <div class="activity-content">
                        <div class="activity-text">You reported a ${item.type} item: ${item.name}</div>
                        <div class="activity-time">${formatDate(item.created_at)}</div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ========================================
// Admin Dashboard
// ========================================

let adminTab = 'items';

async function loadAdminDashboard() {
    try {
        const response = await fetch(`${API_URL}/api/admin/stats`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const stats = await response.json();
        
        document.getElementById('adminUserCount').textContent = stats.total_users || 0;
        document.getElementById('adminLostCount').textContent = stats.lost_items || 0;
        document.getElementById('adminFoundCount').textContent = stats.found_items || 0;
        document.getElementById('adminPendingCount').textContent = stats.pending_claims || 0;
        
        switchAdminTab(adminTab);
    } catch (error) {
        console.error('Error loading admin dashboard:', error);
    }
}

function switchAdminTab(tab) {
    adminTab = tab;
    const tabs = document.querySelectorAll('#adminPage .admin-tabs .tab-btn');
    tabs.forEach(t => {
        t.classList.remove('active');
        if (t.textContent.toLowerCase().includes(tab)) {
            t.classList.add('active');
        }
    });
    
    const content = document.getElementById('adminContent');
    
    if (tab === 'items') {
        fetch(`${API_URL}/api/items`)
            .then(res => res.json())
            .then(items => {
                content.innerHTML = `
                    <div class="admin-table">
                        <table>
                            <thead>
                                <tr><th>Item</th><th>Type</th><th>Category</th><th>Status</th><th>Actions</th></tr>
                            </thead>
                            <tbody>
                                ${items.map(item => `
                                    <tr>
                                        <td>${item.name}</td>
                                        <td><span class="item-badge ${item.type}">${capitalize(item.type)}</span></td>
                                        <td>${capitalize(item.category)}</td>
                                        <td><span class="status-badge ${item.status}">${capitalize(item.status)}</span></td>
                                        <td class="action-buttons">
                                            <button class="approve" onclick="adminResolveItem(${item.id})">Resolve</button>
                                            <button class="delete" onclick="adminDeleteItem(${item.id})">Delete</button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            });
    } else if (tab === 'users') {
        fetch(`${API_URL}/api/admin/users`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(res => res.json())
        .then(users => {
            content.innerHTML = `
                <div class="admin-table">
                    <table>
                        <thead>
                            <tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th></tr>
                        </thead>
                        <tbody>
                            ${users.map(user => `
                                <tr>
                                    <td>${user.name}</td>
                                    <td>${user.email}</td>
                                    <td><span class="status-badge ${user.role === 'admin' ? 'approved' : 'pending'}">${capitalize(user.role)}</span></td>
                                    <td>${formatDate(user.created_at)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        });
    } else if (tab === 'claims') {
        fetch(`${API_URL}/api/admin/claims`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(res => res.json())
        .then(claims => {
            content.innerHTML = `
                <div class="admin-table">
                    <table>
                        <thead>
                            <tr><th>Item</th><th>Claimant</th><th>Status</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${claims.map(claim => `
                                <td>${claim.item_name}</td>
                                    <tdtr>
                                    <>${claim.user_name}</td>
                                    <td><span class="status-badge ${claim.status}">${capitalize(claim.status)}</span></td>
                                    <td class="action-buttons">
                                        ${claim.status === 'pending' ? `
                                            <button class="approve" onclick="adminApproveClaim(${claim.id})">Approve</button>
                                            <button class="reject" onclick="adminRejectClaim(${claim.id})">Reject</button>
                                        ` : ''}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        });
    }
}

async function adminResolveItem(itemId) {
    try {
        await fetch(`${API_URL}/api/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ status: 'resolved' })
        });
        showToast('success', 'Item Resolved', 'Item status updated');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', 'Failed to resolve item');
    }
}

async function adminDeleteItem(itemId) {
    if (!confirm('Delete this item?')) return;
    try {
        await fetch(`${API_URL}/api/items/${itemId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        showToast('success', 'Item Deleted', 'Item has been deleted');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', 'Failed to delete item');
    }
}

async function adminApproveClaim(claimId) {
    try {
        await fetch(`${API_URL}/api/admin/claims/${claimId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ status: 'approved' })
        });
        showToast('success', 'Claim Approved', 'Claim has been approved');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', 'Failed to approve claim');
    }
}

async function adminRejectClaim(claimId) {
    try {
        await fetch(`${API_URL}/api/admin/claims/${claimId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ status: 'rejected' })
        });
        showToast('info', 'Claim Rejected', 'Claim has been rejected');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', 'Failed to reject claim');
    }
}

// ========================================
// Notifications
// ========================================

async function loadNotifications() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_URL}/api/notifications`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();
        
        const list = document.getElementById('notificationList');
        
        if (!data.notifications || data.notifications.length === 0) {
            list.innerHTML = '<div class="empty-state" style="padding: 20px; text-align: center;">No notifications</div>';
            return;
        }
        
        list.innerHTML = data.notifications.map(n => `
            <div class="notification-item ${n.read_status ? '' : 'unread'}">
                <div class="notification-icon ${n.type}">
                    ${n.type === 'lost' ? '🔍' : n.type === 'found' ? '✨' : '📋'}
                </div>
                <div class="notification-content">
                    <div class="notification-text">${n.message}</div>
                    <div class="notification-time">${formatDate(n.created_at)}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    if (!authToken) {
        badge.style.display = 'none';
        return;
    }
    
    fetch(`${API_URL}/api/notifications`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(data => {
        badge.textContent = data.unread_count || 0;
        badge.style.display = data.unread_count > 0 ? 'flex' : 'none';
    })
    .catch(() => {});
}

function markAllRead() {
    if (!authToken) return;
    
    fetch(`${API_URL}/api/notifications/read-all`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(() => loadNotifications())
    .catch(() => {});
}

// ========================================
// Toast Notifications
// ========================================

function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '!'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// ========================================
// Event Listeners
// ========================================

function setupEventListeners() {
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-dropdown')) {
            document.getElementById('dropdownMenu').classList.remove('show');
        }
        if (!e.target.closest('.notification-btn') && !e.target.closest('.notification-panel')) {
            document.getElementById('notificationPanel').classList.add('hidden');
        }
    });
    
    window.addEventListener('scroll', () => {
        const header = document.getElementById('header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAuthModal();
        }
    });
    
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.add('hidden');
            }
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
