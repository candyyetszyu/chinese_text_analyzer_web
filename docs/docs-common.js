// Common JavaScript functionality for all documentation pages

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add copy buttons to code blocks
    addCopyButtons();
    
    // Save checklist progress to localStorage
    saveChecklistProgress();
    
    // Highlight current sidebar item
    highlightCurrentSection();
    
    // Add scroll spy for sidebar
    addScrollSpy();
});

// Copy to clipboard functionality
function addCopyButtons() {
    const codeBlocks = document.querySelectorAll('.code-block');
    codeBlocks.forEach(block => {
        if (!block.querySelector('.copy-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'Copy to clipboard';
            
            copyBtn.addEventListener('click', function() {
                const code = block.querySelector('code');
                const text = code.innerText || code.textContent;
                
                navigator.clipboard.writeText(text).then(function() {
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    copyBtn.style.background = '#28a745';
                    setTimeout(() => {
                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                        copyBtn.style.background = '#6c757d';
                    }, 2000);
                }).catch(function() {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                    copyBtn.style.background = '#28a745';
                    setTimeout(() => {
                        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                        copyBtn.style.background = '#6c757d';
                    }, 2000);
                });
            });
            
            block.appendChild(copyBtn);
        }
    });
}

// Save checklist progress to localStorage
function saveChecklistProgress() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][id^="check"]');
    checkboxes.forEach(checkbox => {
        // Load saved state
        const saved = localStorage.getItem(checkbox.id);
        if (saved === 'true') {
            checkbox.checked = true;
        }
        
        // Save state on change
        checkbox.addEventListener('change', function() {
            localStorage.setItem(this.id, this.checked);
        });
    });
}

// Highlight current section in sidebar
function highlightCurrentSection() {
    const sidebarLinks = document.querySelectorAll('.docs-sidebar a[href^="#"]');
    const sections = document.querySelectorAll('section[id]');
    
    function updateActiveLink() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });
        
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
                link.style.color = '#007bff';
                link.style.fontWeight = 'bold';
            } else {
                link.style.color = '#6c757d';
                link.style.fontWeight = 'normal';
            }
        });
    }
    
    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink(); // Initial call
}

// Add scroll spy functionality
function addScrollSpy() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '-100px 0px -60% 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                const correspondingLink = document.querySelector(`.docs-sidebar a[href="#${id}"]`);
                
                // Remove active class from all links
                document.querySelectorAll('.docs-sidebar a').forEach(link => {
                    link.classList.remove('active');
                    link.style.color = '#6c757d';
                    link.style.fontWeight = 'normal';
                });
                
                // Add active class to current link
                if (correspondingLink) {
                    correspondingLink.classList.add('active');
                    correspondingLink.style.color = '#007bff';
                    correspondingLink.style.fontWeight = 'bold';
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('section[id]').forEach(section => {
        observer.observe(section);
    });
}

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(0, 123, 255, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.background = '';
        navbar.style.backdropFilter = '';
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search (if search exists)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals or clear focus
    if (e.key === 'Escape') {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.tagName !== 'BODY') {
            activeElement.blur();
        }
    }
});

// Add loading states for external links
document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.addEventListener('click', function() {
        this.style.opacity = '0.7';
        this.innerHTML += ' <i class="fas fa-spinner fa-spin"></i>';
    });
});

// Auto-expand code blocks on mobile
function handleMobileCodeBlocks() {
    if (window.innerWidth < 768) {
        document.querySelectorAll('.code-block').forEach(block => {
            block.style.fontSize = '0.875rem';
            block.style.whiteSpace = 'pre-wrap';
        });
    }
}

window.addEventListener('resize', handleMobileCodeBlocks);
handleMobileCodeBlocks(); // Initial call

// Table of contents generator (for pages without sidebar)
function generateTableOfContents() {
    const tocContainer = document.querySelector('#table-of-contents');
    if (!tocContainer) return;
    
    const headings = document.querySelectorAll('h2, h3, h4');
    if (headings.length === 0) return;
    
    const tocList = document.createElement('ul');
    tocList.className = 'list-unstyled';
    
    headings.forEach((heading, index) => {
        const id = heading.id || `heading-${index}`;
        heading.id = id;
        
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = `#${id}`;
        link.textContent = heading.textContent;
        link.className = 'text-decoration-none';
        
        if (heading.tagName === 'H3') {
            listItem.style.marginLeft = '1rem';
        } else if (heading.tagName === 'H4') {
            listItem.style.marginLeft = '2rem';
        }
        
        listItem.appendChild(link);
        tocList.appendChild(listItem);
    });
    
    tocContainer.appendChild(tocList);
}

// Initialize table of contents if container exists
document.addEventListener('DOMContentLoaded', generateTableOfContents);

// Print functionality
function initPrintButton() {
    const printBtn = document.querySelector('#print-docs');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
}

document.addEventListener('DOMContentLoaded', initPrintButton); 