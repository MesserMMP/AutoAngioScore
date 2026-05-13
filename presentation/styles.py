APPLE_STYLE_CSS = """
/* Сбалансированная современная цветовая гамма */
:root {
    --bg-primary: #4f46e5;
    --bg-secondary: #7c3aed;
    --bg-gradient: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    --bg-surface: linear-gradient(135deg, rgba(255,255,255,0.97) 0%, rgba(255,255,255,0.94) 100%);
    
    --accent-cyan: #06b6d4;
    --accent-teal: #3b82f6;
    --accent-purple: #8b5cf6;
    --accent-pink: #d946ef;
    --accent-orange: #f97316;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-yellow: #eab308;
    
    --accent-cyan-light: rgba(6, 182, 212, 0.08);
    --accent-teal-light: rgba(59, 130, 246, 0.08);
    --accent-purple-light: rgba(139, 92, 246, 0.08);
    --accent-pink-light: rgba(217, 70, 239, 0.08);
    --accent-green-light: rgba(16, 185, 129, 0.08);
    --accent-red-light: rgba(239, 68, 68, 0.08);
    --accent-orange-light: rgba(249, 115, 22, 0.08);
    
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-light: #94a3b8;
    --text-white: #ffffff;
    
    --border-color: rgba(255, 255, 255, 0.2);
    --border-dark: rgba(0, 0, 0, 0.06);
    --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    --shadow-glow: 0 0 0 3px rgba(6, 182, 212, 0.2);
    --shadow-glow-purple: 0 0 0 3px rgba(139, 92, 246, 0.2);
}

* {
    font-family: -apple-system, "SF Pro Text", "SF Pro Display", "Inter", "Helvetica Neue", system-ui, sans-serif;
}

body, .gradio-container {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%) !important;
    position: relative;
}

body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.gradio-container {
    position: relative;
    z-index: 1;
}

.gr-box, .gr-form, .panel, .tabs, .tab-nav, .accordion {
    background: transparent !important;
    border: none !important;
}

.apple-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

.apple-header {
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    padding: 1rem 0;
}

.apple-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.apple-subtitle {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.85);
    margin-top: 0.5rem;
    font-weight: 400;
}

.apple-card {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.apple-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    background: rgba(255, 255, 255, 0.98);
}

.apple-card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.2) 100%);
}

.apple-card-title {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.apple-card-content {
    padding: 1.5rem;
}

.add-study-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.96) 100%);
    border: 1px solid rgba(255,255,255,0.4);
    position: relative;
    overflow: hidden;
}

.apple-button {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: white;
    border: none;
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
}

.apple-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.apple-button:hover::before {
    left: 100%;
}

.apple-button:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, #0891b2 0%, #2563eb 100%);
}

.apple-button-add {
    background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    color: white;
    border: none;
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
}

.apple-button-add::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.apple-button-add:hover::before {
    left: 100%;
}

.apple-button-add:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
}

.apple-button-clear {
    background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
    color: white;
    border: none;
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
}

.apple-button-clear::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.apple-button-clear:hover::before {
    left: 100%;
}

.apple-button-clear:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, #ea580c 0%, #eab308 100%);
}

.apple-input {
    border: 1.5px solid rgba(0, 0, 0, 0.05) !important;
    border-radius: 14px !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.9375rem !important;
    background: rgba(255, 255, 255, 0.95) !important;
    transition: all 0.3s ease !important;
}

.apple-input:focus {
    outline: none !important;
    border-color: #06b6d4 !important;
    box-shadow: var(--shadow-glow) !important;
    background: white !important;
}

.apple-table {
    border-radius: 16px;
    overflow: hidden;
    border: none;
}

.apple-table table {
    background: rgba(255, 255, 255, 0.95) !important;
    border-collapse: collapse !important;
    width: 100%;
}

.apple-table th {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 12px 16px !important;
    border-bottom: none !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
}

.apple-table td {
    background: rgba(255, 255, 255, 0.98) !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
}

.apple-table tr:last-child td {
    border-bottom: none !important;
}

.apple-table tr:hover td {
    background: rgba(139, 92, 246, 0.04) !important;
}

.queue-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border-radius: 16px;
    box-shadow: var(--shadow-sm);
}

.queue-table thead th {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: #ffffff;
    font-size: 0.875rem;
    font-weight: 700;
    text-align: left;
    padding: 0.9rem 1rem;
    border-bottom: none;
}

.queue-table tbody td {
    background: rgba(255, 255, 255, 0.98);
    color: var(--text-primary);
    padding: 0.9rem 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    vertical-align: top;
}

.queue-table tbody tr:last-child td {
    border-bottom: none;
}

.queue-table tbody tr:hover td {
    background: rgba(139, 92, 246, 0.04);
}

.queue-empty {
    padding: 1rem;
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8125rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-running {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

.status-done {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

.status-error {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

.status-queued {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

@keyframes pulse {
    0%, 100% { 
        opacity: 1;
        transform: scale(1);
    }
    50% { 
        opacity: 0.85;
        transform: scale(1.02);
    }
}

.pulse {
    animation: pulse 1.5s ease-in-out infinite;
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #0891b2 0%, #2563eb 100%);
}

.upload-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.instruction-box {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.06) 0%, rgba(6, 182, 212, 0.06) 100%);
    border-radius: 16px;
    padding: 1rem;
    margin-top: 1rem;
    border: 1px solid rgba(139, 92, 246, 0.15);
    backdrop-filter: blur(10px);
}

.instruction-title {
    font-size: 0.875rem;
    font-weight: 700;
    background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.instruction-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
}

.instruction-list li {
    font-size: 0.8125rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
}

@media (max-width: 768px) {
    .upload-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .instruction-list {
        grid-template-columns: 1fr;
    }
    
    .apple-title {
        font-size: 2rem;
    }
}
"""
