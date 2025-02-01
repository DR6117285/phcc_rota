from flask import render_template, send_file, Blueprint, request, jsonify
from src.services.enhanced_report_service import EnhancedReportService
import logging

logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__)
report_service = EnhancedReportService()

@report_bp.route('/report')
def show_report():
    """Display the enhanced schedule report."""
    try:
        # Get filter parameters
        filters = {
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'team': request.args.get('team'),
            'staff_id': request.args.get('staff_id'),
            'shift_type': request.args.get('shift_type')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        report_data = report_service.generate_detailed_report(filters=filters)
        return render_template('report.html', report=report_data, filters=filters)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return render_template('error.html', 
                             error_message="Failed to generate report. Please try again later."), 500

@report_bp.route('/report/export')
def export_report():
    """Export the report data to Excel."""
    try:
        # Get filter parameters
        filters = {
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'team': request.args.get('team'),
            'staff_id': request.args.get('staff_id'),
            'shift_type': request.args.get('shift_type')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        excel_file = report_service.export_to_excel(filters=filters)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='schedule_report.xlsx'
        )
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to export report. Please try again later.'}), 500

@report_bp.route('/report/teams')
def get_teams():
    """Get list of available teams for filtering."""
    try:
        teams = report_service.get_available_teams()
        return jsonify(teams)
    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch teams.'}), 500

@report_bp.route('/report/staff')
def get_staff():
    """Get list of available staff for filtering."""
    try:
        staff = report_service.get_available_staff()
        return jsonify(staff)
    except Exception as e:
        logger.error(f"Error fetching staff: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch staff.'}), 500 