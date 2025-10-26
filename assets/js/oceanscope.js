// OceanScope Interactive Designer

class OceanDesigner {
    constructor() {
        this.canvas = document.getElementById('ocean-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 5; // pixels per cell
        this.gridWidth = Math.floor(this.canvas.width / this.gridSize);
        this.gridHeight = Math.floor(this.canvas.height / this.gridSize);

        // Grid data: {type: 'sand'|'ocean'|'pier', depth: number}
        this.grid = Array(this.gridHeight).fill(null).map(() =>
            Array(this.gridWidth).fill(null).map(() => ({ type: null, depth: 0 }))
        );

        this.currentTool = 'sand';
        this.brushSize = 3;
        this.currentDepth = 5.0;
        this.isDrawing = false;
        this.pierCells = new Set();

        this.initializeEventListeners();
        this.render();
    }

    initializeEventListeners() {
        // Tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentTool = e.target.dataset.tool;
            });
        });

        // Brush size
        const brushSize = document.getElementById('brush-size');
        const brushSizeValue = document.getElementById('brush-size-value');
        brushSize.addEventListener('input', (e) => {
            this.brushSize = parseInt(e.target.value);
            brushSizeValue.textContent = this.brushSize;
        });

        // Depth slider
        const depthSlider = document.getElementById('depth-slider');
        const depthValue = document.getElementById('depth-value');
        depthSlider.addEventListener('input', (e) => {
            this.currentDepth = parseFloat(e.target.value);
            depthValue.textContent = this.currentDepth.toFixed(1) + 'm';
        });

        // Canvas drawing
        this.canvas.addEventListener('mousedown', (e) => {
            this.isDrawing = true;
            this.paint(e);
        });

        this.canvas.addEventListener('mousemove', (e) => {
            this.updateCursorInfo(e);
            if (this.isDrawing) {
                this.paint(e);
            }
        });

        this.canvas.addEventListener('mouseup', () => {
            this.isDrawing = false;
            this.updateStats();
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.isDrawing = false;
            document.getElementById('cursor-info').style.display = 'none';
        });

        this.canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });

        // Action buttons
        document.getElementById('clear-btn').addEventListener('click', () => {
            if (confirm('Clear all design?')) {
                this.clearAll();
            }
        });

        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportDesign();
        });
    }

    getGridCoords(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) * (this.canvas.width / rect.width) / this.gridSize);
        const y = Math.floor((e.clientY - rect.top) * (this.canvas.height / rect.height) / this.gridSize);
        return { x, y };
    }

    paint(e) {
        const { x, y } = this.getGridCoords(e);
        const isErase = e.button === 2 || this.currentTool === 'erase';

        for (let dy = -this.brushSize; dy <= this.brushSize; dy++) {
            for (let dx = -this.brushSize; dx <= this.brushSize; dx++) {
                const nx = x + dx;
                const ny = y + dy;

                if (nx >= 0 && nx < this.gridWidth && ny >= 0 && ny < this.gridHeight) {
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist <= this.brushSize) {
                        if (isErase) {
                            const cell = this.grid[ny][nx];
                            if (cell.type === 'pier') {
                                this.pierCells.delete(`${nx},${ny}`);
                            }
                            this.grid[ny][nx] = { type: null, depth: 0 };
                        } else {
                            const depth = this.currentTool === 'ocean' ? this.currentDepth : 0;
                            this.grid[ny][nx] = { type: this.currentTool, depth };

                            if (this.currentTool === 'pier') {
                                this.pierCells.add(`${nx},${ny}`);
                            }
                        }
                    }
                }
            }
        }

        this.render();
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const cell = this.grid[y][x];

                if (cell.type) {
                    let color;
                    if (cell.type === 'sand') {
                        color = '#f4e4c1';
                    } else if (cell.type === 'ocean') {
                        // Color based on depth
                        const depthRatio = Math.min(cell.depth / 20, 1);
                        const r = Math.floor(30 + (10 - 30) * depthRatio);
                        const g = Math.floor(144 + (30 - 144) * depthRatio);
                        const b = Math.floor(255 + (80 - 255) * depthRatio);
                        color = `rgb(${r}, ${g}, ${b})`;
                    } else if (cell.type === 'pier') {
                        color = '#8b4513';
                    }

                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(
                        x * this.gridSize,
                        y * this.gridSize,
                        this.gridSize,
                        this.gridSize
                    );
                }
            }
        }

        // Draw grid lines (subtle)
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.lineWidth = 0.5;
        for (let x = 0; x <= this.gridWidth; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.gridSize, 0);
            this.ctx.lineTo(x * this.gridSize, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.gridHeight; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.gridSize);
            this.ctx.lineTo(this.canvas.width, y * this.gridSize);
            this.ctx.stroke();
        }
    }

    updateCursorInfo(e) {
        const { x, y } = this.getGridCoords(e);
        const cursorInfo = document.getElementById('cursor-info');

        if (x >= 0 && x < this.gridWidth && y >= 0 && y < this.gridHeight) {
            const cell = this.grid[y][x];
            let info = `(${x}, ${y})`;
            if (cell.type) {
                info += ` - ${cell.type}`;
                if (cell.type === 'ocean') {
                    info += ` ${cell.depth.toFixed(1)}m`;
                }
            }

            cursorInfo.textContent = info;
            cursorInfo.style.display = 'block';
            cursorInfo.style.left = (e.clientX + 15) + 'px';
            cursorInfo.style.top = (e.clientY + 15) + 'px';
        }
    }

    updateStats() {
        let cellsPainted = 0;
        let minDepth = Infinity;
        let maxDepth = 0;

        for (let y = 0; y < this.gridHeight; y++) {
            for (let x = 0; x < this.gridWidth; x++) {
                const cell = this.grid[y][x];
                if (cell.type) {
                    cellsPainted++;
                    if (cell.type === 'ocean') {
                        minDepth = Math.min(minDepth, cell.depth);
                        maxDepth = Math.max(maxDepth, cell.depth);
                    }
                }
            }
        }

        document.getElementById('cells-painted').textContent = cellsPainted;
        document.getElementById('depth-range').textContent =
            minDepth === Infinity ? '0m - 0m' : `${minDepth.toFixed(1)}m - ${maxDepth.toFixed(1)}m`;
        document.getElementById('pier-count').textContent = this.pierCells.size;
    }

    clearAll() {
        this.grid = Array(this.gridHeight).fill(null).map(() =>
            Array(this.gridWidth).fill(null).map(() => ({ type: null, depth: 0 }))
        );
        this.pierCells.clear();
        this.render();
        this.updateStats();
    }

    async exportDesign() {
        const design = {
            width: this.gridWidth,
            height: this.gridHeight,
            gridSize: this.gridSize,
            grid: this.grid,
            timestamp: new Date().toISOString()
        };

        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(design)
            });

            const result = await response.json();

            if (result.success) {
                alert(`Design exported successfully!\nSaved to: ${result.filename}`);
            } else {
                alert('Export failed: ' + result.error);
            }
        } catch (error) {
            console.error('Export error:', error);
            alert('Export failed. Check console for details.');
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new OceanDesigner();
});
