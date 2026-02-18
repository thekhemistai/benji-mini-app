// 🧪 Khemist Lab Dashboard
// Real-time task management with drag & drop

class LabDashboard {
    constructor() {
        this.tasks = [];
        this.draggedTask = null;
        this.init();
    }

    init() {
        this.loadTasks();
        this.setupEventListeners();
        this.startClock();
        this.createParticles();
        this.render();
        
        // Auto-refresh every 30 seconds
        setInterval(() => this.refreshStats(), 30000);
    }

    // Sample tasks - replace with real data from your files
    loadTasks() {
        this.tasks = [
            {
                id: '1',
                title: 'Paper Trading BTC Strategy',
                desc: 'Monitor 1h/4h Polymarket markets, log 10 opportunities',
                status: 'working',
                priority: 'high',
                created: new Date(),
                tags: ['trading', 'btc']
            },
            {
                id: '2',
                title: 'Review AGENTLOG MVP',
                desc: 'Run Hardhat tests, fix any failures',
                status: 'pending',
                priority: 'high',
                created: new Date(),
                tags: ['dev', 'agentlog']
            },
            {
                id: '3',
                title: 'Track CONWAY Position',
                desc: 'Monitor $20 position, alert on 25%+ moves',
                status: 'working',
                priority: 'medium',
                created: new Date(),
                tags: ['conway', 'tracking']
            },
            {
                id: '4',
                title: 'Build Visual Lab GUI',
                desc: 'Create animated dashboard with drag & drop',
                status: 'finished',
                priority: 'high',
                created: new Date(),
                completed: new Date(),
                tags: ['ui', 'dashboard']
            },
            {
                id: '5',
                title: 'Spawn Counterweight Review',
                desc: 'Review completed work with Shadow Council',
                status: 'pending',
                priority: 'medium',
                tags: ['council', 'review']
            },
            {
                id: '6',
                title: 'Fund Bankr Wallet',
                desc: 'Send $5-10 ETH to 0x1e6ab... for live trading',
                status: 'pending',
                priority: 'high',
                needsUser: true,
                tags: ['wallet', 'trading']
            }
        ];
    }

    setupEventListeners() {
        // Drag and drop setup
        const columns = document.querySelectorAll('.column');
        
        columns.forEach(column => {
            column.addEventListener('dragover', (e) => this.handleDragOver(e));
            column.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            column.addEventListener('drop', (e) => this.handleDrop(e));
        });
    }

    createParticles() {
        const container = document.getElementById('particles');
        const particleCount = 50;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (15 + Math.random() * 10) + 's';
            container.appendChild(particle);
        }
    }

    startClock() {
        const updateClock = () => {
            const now = new Date();
            document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        };
        updateClock();
        setInterval(updateClock, 1000);
    }

    render() {
        this.renderTasks();
        this.updateCounts();
        this.refreshStats();
    }

    renderTasks() {
        const columns = {
            pending: document.getElementById('pending-tasks'),
            working: document.getElementById('working-tasks'),
            finished: document.getElementById('finished-tasks')
        };

        // Clear columns
        Object.values(columns).forEach(col => col.innerHTML = '');

        // Sort tasks by priority
        const priorityOrder = { high: 0, medium: 1, low: 2 };
        this.tasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

        // Render each task
        this.tasks.forEach(task => {
            const card = this.createTaskCard(task);
            columns[task.status].appendChild(card);
        });
    }

    createTaskCard(task) {
        const card = document.createElement('div');
        card.className = `task-card priority-${task.priority}`;
        card.draggable = true;
        card.dataset.taskId = task.id;

        const needsUserBadge = task.needsUser ? '<span class="user-badge">👤</span>' : '';

        card.innerHTML = `
            <div class="task-header">
                <span class="task-title">${task.title}</span>
                <span class="task-priority">${task.priority}</span>
            </div>
            <div class="task-desc">${task.desc}</div>
            <div class="task-meta">
                <div class="task-status">
                    <span class="status-dot ${task.status === 'working' ? 'active' : task.status === 'pending' ? 'waiting' : 'done'}"></span>
                    ${task.status === 'working' ? 'In Progress' : task.status === 'pending' ? 'Waiting' : 'Complete'}
                    ${needsUserBadge}
                </div>
                <span>${task.tags.map(t => '#' + t).join(' ')}</span>
            </div>
        `;

        // Drag events
        card.addEventListener('dragstart', (e) => this.handleDragStart(e, task));
        card.addEventListener('dragend', (e) => this.handleDragEnd(e));

        return card;
    }

    handleDragStart(e, task) {
        this.draggedTask = task;
        e.target.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    }

    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        this.draggedTask = null;
        
        // Remove drag-over from all columns
        document.querySelectorAll('.column').forEach(col => {
            col.classList.remove('drag-over');
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.currentTarget.classList.remove('drag-over');
    }

    handleDrop(e) {
        e.preventDefault();
        const column = e.currentTarget;
        column.classList.remove('drag-over');

        if (this.draggedTask) {
            const newStatus = column.dataset.column;
            
            // Update task status
            this.draggedTask.status = newStatus;
            if (newStatus === 'finished') {
                this.draggedTask.completed = new Date();
            }

            // Save and re-render
            this.saveTasks();
            this.render();

            // Visual feedback
            this.showNotification(`Moved "${this.draggedTask.title}" to ${newStatus}`);
        }
    }

    updateCounts() {
        const counts = {
            pending: this.tasks.filter(t => t.status === 'pending').length,
            working: this.tasks.filter(t => t.status === 'working').length,
            finished: this.tasks.filter(t => t.status === 'finished').length
        };

        document.getElementById('pending-count').textContent = counts.pending;
        document.getElementById('working-count').textContent = counts.working;
        document.getElementById('finished-count').textContent = counts.finished;
        document.getElementById('active-tasks').textContent = counts.working;

        // Count completed today
        const today = new Date().toDateString();
        const completedToday = this.tasks.filter(t => 
            t.status === 'finished' && 
            t.completed && 
            new Date(t.completed).toDateString() === today
        ).length;
        document.getElementById('completed-today').textContent = completedToday;
    }

    refreshStats() {
        // Fetch paper trading stats from localStorage or API
        const stats = this.getTradingStats();
        
        document.getElementById('win-rate').textContent = stats.winRate + '%';
        
        const pnlElement = document.getElementById('total-pnl');
        pnlElement.textContent = (stats.pnl >= 0 ? '+' : '') + '$' + stats.pnl.toFixed(2);
        pnlElement.className = 'metric-value ' + (stats.pnl >= 0 ? 'positive' : 'negative');
    }

    getTradingStats() {
        // Placeholder - replace with real data from your paper trading logs
        return {
            winRate: 0,
            pnl: 0,
            trades: 0
        };
    }

    saveTasks() {
        // In a real implementation, save to file or API
        localStorage.setItem('labTasks', JSON.stringify(this.tasks));
    }

    showNotification(message) {
        // Simple notification - could be enhanced
        console.log('🔬 Lab:', message);
    }

    // Public methods for external use
    addTask(task) {
        task.id = Date.now().toString();
        task.created = new Date();
        this.tasks.push(task);
        this.saveTasks();
        this.render();
    }

    updateTaskStatus(taskId, newStatus) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.status = newStatus;
            if (newStatus === 'finished') {
                task.completed = new Date();
            }
            this.saveTasks();
            this.render();
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.labDashboard = new LabDashboard();
    console.log('🧪 Khemist Lab Dashboard initialized');
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LabDashboard;
}
