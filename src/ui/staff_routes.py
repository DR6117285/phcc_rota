from flask import Blueprint, render_template, request, jsonify
from src.services.staff_management_service import StaffManagementService, SkillLevel
import logging

logger = logging.getLogger(__name__)
staff_bp = Blueprint('staff', __name__)
staff_service = StaffManagementService()

@staff_bp.route('/staff')
def staff_list():
    """Display staff management page."""
    try:
        staff_members = list(staff_service.staff_profiles.values())
        teams = [{'id': team_id, 'name': team_id} for team_id in staff_service.teams.keys()]
        
        # Calculate statistics
        stats = {
            'total_staff': len(staff_members),
            'total_teams': len(staff_service.teams),
            'total_skills': len(staff_service.skills_registry),
            'total_certifications': len(staff_service.certifications_registry)
        }
        
        # Calculate team distribution for chart
        team_distribution = {
            'labels': list(staff_service.teams.keys()),
            'data': [len(members) for members in staff_service.teams.values()]
        }
        
        return render_template('staff.html',
                             staff_members=staff_members,
                             teams=teams,
                             stats=stats,
                             team_distribution=team_distribution)
    except Exception as e:
        logger.error(f"Error displaying staff list: {str(e)}", exc_info=True)
        return render_template('error.html',
                             error_message="Failed to load staff management page."), 500

@staff_bp.route('/staff', methods=['POST'])
def add_staff():
    """Add a new staff member."""
    try:
        staff_data = request.get_json()
        staff_id = staff_service.add_staff_member(staff_data)
        return jsonify({'id': staff_id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding staff member: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to add staff member.'}), 500

@staff_bp.route('/staff/<staff_id>', methods=['GET'])
def get_staff(staff_id):
    """Get staff member details."""
    try:
        staff = staff_service.get_staff_member(staff_id)
        return jsonify(staff)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting staff member: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get staff member details.'}), 500

@staff_bp.route('/staff/<staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update staff member details."""
    try:
        updates = request.get_json()
        staff = staff_service.update_staff_member(staff_id, updates)
        return jsonify(staff)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating staff member: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update staff member.'}), 500

@staff_bp.route('/staff/<staff_id>/skills', methods=['POST'])
def add_skill(staff_id):
    """Add a skill to staff member."""
    try:
        data = request.get_json()
        staff_service.add_skill(
            staff_id,
            data['skill_name'],
            SkillLevel(data['level'])
        )
        return jsonify({'message': 'Skill added successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding skill: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to add skill.'}), 500

@staff_bp.route('/staff/<staff_id>/certifications', methods=['POST'])
def add_certification(staff_id):
    """Add a certification to staff member."""
    try:
        data = request.get_json()
        staff_service.add_certification(
            staff_id,
            data['certification'],
            data.get('expiry_date')
        )
        return jsonify({'message': 'Certification added successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding certification: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to add certification.'}), 500

@staff_bp.route('/staff/<staff_id>/availability', methods=['POST'])
def update_availability(staff_id):
    """Update staff member availability."""
    try:
        data = request.get_json()
        staff_service.update_availability(
            staff_id,
            data['availability_type'],
            set(data['dates']),
            data['is_available']
        )
        return jsonify({'message': 'Availability updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating availability: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update availability.'}), 500

@staff_bp.route('/staff/<staff_id>/preferences', methods=['POST'])
def update_preferences(staff_id):
    """Update staff member preferences."""
    try:
        data = request.get_json()
        staff_service.update_preferences(
            staff_id,
            data['preference_type'],
            set(data['preferences'])
        )
        return jsonify({'message': 'Preferences updated successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to update preferences.'}), 500

@staff_bp.route('/staff/available', methods=['GET'])
def get_available_staff():
    """Get available staff for a given date and shift type."""
    try:
        date = request.args.get('date')
        shift_type = request.args.get('shift_type')
        
        if not date:
            return jsonify({'error': 'Date parameter is required'}), 400
            
        available_staff = staff_service.get_available_staff(date, shift_type)
        return jsonify(available_staff)
    except Exception as e:
        logger.error(f"Error getting available staff: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get available staff.'}), 500

@staff_bp.route('/staff/skills/<skill_name>')
def get_staff_with_skill(skill_name):
    """Get staff members with a specific skill."""
    try:
        min_level = request.args.get('min_level')
        min_level = SkillLevel(min_level) if min_level else None
        
        qualified_staff = staff_service.get_staff_with_skill(skill_name, min_level)
        return jsonify(qualified_staff)
    except Exception as e:
        logger.error(f"Error getting staff with skill: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get staff with skill.'}), 500

@staff_bp.route('/staff/certifications/<certification>')
def get_staff_with_certification(certification):
    """Get staff members with a specific certification."""
    try:
        certified_staff = staff_service.get_staff_with_certification(certification)
        return jsonify(certified_staff)
    except Exception as e:
        logger.error(f"Error getting staff with certification: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get staff with certification.'}), 500 