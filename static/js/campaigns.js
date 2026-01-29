/**
 * UDAAN SOCIETY - CAMPAIGNS PAGE
 * Main JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initMobileMenu();
    initFilters();
    initSearch();
    initSort();
    initStatsCounter();
    initProgressBars();
    initPagination();
});

/* ============================================
   MOBILE MENU
   ============================================ */

function initMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.getElementById('navLinks');
    
    if (!mobileMenu || !navLinks) return;
    
    mobileMenu.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        const icon = mobileMenu.querySelector('i');
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!mobileMenu.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('active');
            const icon = mobileMenu.querySelector('i');
            icon.classList.add('fa-bars');
            icon.classList.remove('fa-times');
        }
    });
}

/* ============================================
   FILTER FUNCTIONALITY
   ============================================ */

function initFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const campaignCards = document.querySelectorAll('.campaign-card');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.dataset.filter;
            
            // Filter cards with animation
            campaignCards.forEach((card, index) => {
                const category = card.dataset.category;
                const shouldShow = filter === 'all' || category === filter;
                
                if (shouldShow) {
                    card.style.display = 'block';
                    // Staggered animation
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 50);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
            
            checkNoResults();
        });
    });
}

/* ============================================
   SEARCH FUNCTIONALITY
   ============================================ */

function initSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    let debounceTimer;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            performSearch(e.target.value.toLowerCase());
        }, 300);
    });
}

function performSearch(term) {
    const campaignCards = document.querySelectorAll('.campaign-card');
    
    campaignCards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const desc = card.querySelector('.card-description').textContent.toLowerCase();
        const category = card.dataset.category.toLowerCase();
        
        const matches = title.includes(term) || 
                       desc.includes(term) || 
                       category.includes(term);
        
        card.style.display = matches ? 'block' : 'none';
    });
    
    checkNoResults();
}

/* ============================================
   SORT FUNCTIONALITY
   ============================================ */

function initSort() {
    const sortSelect = document.getElementById('sortSelect');
    const grid = document.getElementById('campaignsGrid');
    
    if (!sortSelect || !grid) return;
    
    sortSelect.addEventListener('change', () => {
        const cards = Array.from(grid.querySelectorAll('.campaign-card'));
        const sortValue = sortSelect.value;
        
        cards.sort((a, b) => {
            const goalA = parseInt(a.dataset.goal);
            const goalB = parseInt(b.dataset.goal);
            const raisedA = parseInt(a.dataset.raised);
            const raisedB = parseInt(b.dataset.raised);
            const dateA = new Date(a.dataset.date);
            const dateB = new Date(b.dataset.date);
            const progressA = (raisedA / goalA) * 100;
            const progressB = (raisedB / goalB) * 100;
            
            switch(sortValue) {
                case 'newest':
                    return dateB - dateA;
                case 'oldest':
                    return dateA - dateB;
                case 'goal-high':
                    return goalB - goalA;
                case 'goal-low':
                    return goalA - goalB;
                case 'progress':
                    return progressB - progressA;
                default:
                    return 0;
            }
        });
        
        // Re-append in sorted order with animation
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                grid.appendChild(card);
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
            }, index * 30);
        });
    });
}

/* ============================================
   STATS COUNTER ANIMATION
   ============================================ */

function initStatsCounter() {
    const stats = document.querySelectorAll('.stat-number');
    if (stats.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = 2000;
    const frameDuration = 1000 / 60;
    const totalFrames = Math.round(duration / frameDuration);
    const easeOutQuad = t => t * (2 - t);
    
    let frame = 0;
    
    const counter = setInterval(() => {
        frame++;
        const progress = easeOutQuad(frame / totalFrames);
        const current = Math.round(target * progress);
        
        // Format number
        element.textContent = formatNumber(current);
        
        if (frame === totalFrames) {
            clearInterval(counter);
            element.textContent = formatNumber(target);
        }
    }, frameDuration);
}

function formatNumber(num) {
    if (num >= 10000000) {
        return (num / 10000000).toFixed(1) + 'Cr';
    } else if (num >= 100000) {
        return (num / 100000).toFixed(1) + 'L';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

/* ============================================
   PROGRESS BAR ANIMATION
   ============================================ */

function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    if (progressBars.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const targetWidth = bar.dataset.progress + '%';
                
                // Start from 0 and animate to target
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.width = targetWidth;
                }, 100);
                
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.5 });
    
    progressBars.forEach(bar => observer.observe(bar));
}

/* ============================================
   PAGINATION
   ============================================ */

function initPagination() {
    const pageBtns = document.querySelectorAll('.page-btn');
    
    pageBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.querySelector('i')) return; // Skip arrows for now
            
            pageBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Scroll to top of campaigns
            document.querySelector('.campaigns-section').scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

function checkNoResults() {
    const cards = document.querySelectorAll('.campaign-card');
    const noResults = document.getElementById('noResults');
    const pagination = document.querySelector('.pagination');
    
    const visibleCards = Array.from(cards).filter(c => c.style.display !== 'none');
    
    if (visibleCards.length === 0) {
        noResults.style.display = 'block';
        if (pagination) pagination.style.display = 'none';
    } else {
        noResults.style.display = 'none';
        if (pagination) pagination.style.display = 'flex';
    }
}

function resetFilters() {
    // Reset filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === 'all') {
            btn.classList.add('active');
        }
    });
    
    // Reset search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = '';
    
    // Show all cards
    document.querySelectorAll('.campaign-card').forEach(card => {
        card.style.display = 'block';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    });
    
    checkNoResults();
}

/* ============================================
   QUICK DONATE & TOAST
   ============================================ */

function quickDonate(campaignName) {
    showToast(`Thanks for your interest in "${campaignName}"! Redirecting to donation page...`);
    
    // Simulate redirect
    setTimeout(() => {
        console.log(`Redirecting to donation page for: ${campaignName}`);
        // window.location.href = `/donate?campaign=${encodeURIComponent(campaignName)}`;
    }, 1500);
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!toast || !toastMessage) return;
    
    toastMessage.textContent = message;
    toast.className = `toast ${type}`;
    
    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    // Auto dismiss
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/* ============================================
   SMOOTH SCROLL POLYFILL (optional)
   ============================================ */

// Add smooth scroll behavior for older browsers
if (!('scrollBehavior' in document.documentElement.style)) {
    import('https://cdn.jsdelivr.net/npm/smoothscroll-polyfill@0.4.4/dist/smoothscroll.min.js')
        .then(() => {
            window.smoothscroll.polyfill();
        })
        .catch(() => {
            // Silently fail - native scroll will work
        });
}