"""Flask app for OceanScope GUI."""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import webbrowser
from threading import Timer


app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent.parent.parent / 'assets' / 'templates'),
    static_folder=str(Path(__file__).parent.parent.parent / 'assets'),
    static_url_path='/static'
)


@app.route('/')
def index():
    """Serve the OceanScope GUI."""
    return render_template('oceanscope.html')


@app.route('/api/export', methods=['POST'])
def export_design():
    """Export ocean design to JSON file."""
    try:
        design_data = request.get_json()

        # Create ocean_designs directory if it doesn't exist
        designs_dir = Path(__file__).parent.parent.parent / 'ocean_designs'
        designs_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ocean_design_{timestamp}.json'
        filepath = designs_dir / filename

        # Save design
        with open(filepath, 'w') as f:
            json.dump(design_data, f, indent=2)

        return jsonify({
            'success': True,
            'filename': str(filepath),
            'message': 'Design exported successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/designs', methods=['GET'])
def list_designs():
    """List all saved ocean designs."""
    try:
        designs_dir = Path(__file__).parent.parent.parent / 'ocean_designs'
        if not designs_dir.exists():
            return jsonify({'designs': []})

        designs = []
        for file in designs_dir.glob('*.json'):
            designs.append({
                'filename': file.name,
                'path': str(file),
                'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })

        designs.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'designs': designs})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    """Open browser after a short delay."""
    webbrowser.open('http://127.0.0.1:5000/')


def main():
    """Run the OceanScope app."""
    print("\n" + "="*60)
    print("🌊 OceanScope - Beach Designer")
    print("="*60)
    print("\nStarting server...")
    print("Opening browser at http://127.0.0.1:5000/")
    print("\nPress Ctrl+C to stop the server\n")

    # Open browser after 1 second
    Timer(1, open_browser).start()

    # Run Flask app
    app.run(debug=False, port=5000)


if __name__ == '__main__':
    main()
