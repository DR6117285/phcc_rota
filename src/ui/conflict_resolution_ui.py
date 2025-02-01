from flask import Flask, render_template, jsonify, request
from typing import Dict, List, Any
import logging

from ..services.conflict_resolver import ConflictResolver
from ..core.staff_manager import StaffManager
from ..core.shift_allocator import ShiftAllocator

logger = logging.getLogger(__name__)

class ConflictResolutionUI:
    def __init__(self):
        self.app = Flask(__name__)
        self.conflict_resolver = ConflictResolver()
        self.staff_manager = StaffManager()
        self.shift_allocator = ShiftAllocator()
        
        # Register routes
        self.register_routes()
    
    def register_routes(self):
        """Register all UI routes"""
        
        @self.app.route('/conflicts')
        def list_conflicts():
            """Display current conflicts with resolution options"""
            schedule = self._get_current_schedule()
            conflicts = self.conflict_resolver.detect_conflicts(schedule)
            
            return render_template(
                'conflicts.html',
                conflicts=conflicts,
                schedule=schedule
            )
        
        @self.app.route('/conflicts/<conflict_id>/details')
        def conflict_details(conflict_id: str):
            """Show detailed information about a specific conflict"""
            schedule = self._get_current_schedule()
            conflicts = self.conflict_resolver.detect_conflicts(schedule)
            conflict = next((c for c in conflicts if c.id == conflict_id), None)
            
            if not conflict:
                return jsonify({'error': 'Conflict not found'}), 404
            
            analysis = self.conflict_resolver.analyze_conflict(conflict)
            resolutions = self.conflict_resolver.suggest_resolutions(conflict)
            
            return render_template(
                'conflict_details.html',
                conflict=conflict,
                analysis=analysis,
                resolutions=resolutions
            )
        
        @self.app.route('/conflicts/<conflict_id>/resolve', methods=['POST'])
        def resolve_conflict(conflict_id: str):
            """Handle conflict resolution"""
            schedule = self._get_current_schedule()
            conflicts = self.conflict_resolver.detect_conflicts(schedule)
            conflict = next((c for c in conflicts if c.id == conflict_id), None)
            
            if not conflict:
                return jsonify({'error': 'Conflict not found'}), 404
            
            resolution_data = request.json
            if not resolution_data:
                return jsonify({'error': 'No resolution data provided'}), 400
            
            # Validate resolution
            errors = self.conflict_resolver.validate_manual_resolution(
                conflict, resolution_data
            )
            if errors:
                return jsonify({'errors': errors}), 400
            
            # Apply resolution
            success = self.conflict_resolver.apply_resolution(
                conflict, resolution_data
            )
            
            if not success:
                return jsonify({'error': 'Failed to apply resolution'}), 500
            
            return jsonify({'status': 'success'})
        
        @self.app.route('/conflicts/impact-analysis', methods=['POST'])
        def analyze_impact():
            """Analyze impact of proposed resolution"""
            resolution_data = request.json
            if not resolution_data:
                return jsonify({'error': 'No resolution data provided'}), 400
            
            schedule = self._get_current_schedule()
            conflicts = self.conflict_resolver.detect_conflicts(schedule)
            conflict = next((c for c in conflicts if c.id == resolution_data['conflict_id']), None)
            
            if not conflict:
                return jsonify({'error': 'Conflict not found'}), 404
            
            impact = self.conflict_resolver.get_staff_impact(
                conflict, resolution_data['resolution']
            )
            
            return jsonify(impact)
        
        @self.app.route('/conflicts/history')
        def resolution_history():
            """Show resolution history"""
            schedule = self._get_current_schedule()
            history = self.conflict_resolver.get_resolution_history(schedule)
            
            return render_template(
                'resolution_history.html',
                history=history
            )
    
    def _get_current_schedule(self) -> Dict[str, Any]:
        """Get the current schedule state"""
        # This would be replaced with actual schedule retrieval logic
        return self.shift_allocator.get_current_schedule()
    
    def run(self, host: str = 'localhost', port: int = 5000, debug: bool = False):
        """Run the UI server"""
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    ui = ConflictResolutionUI()
    ui.run(debug=True) 