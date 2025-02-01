import pytest
from playwright.sync_api import Page, expect
from ..ui.conflict_resolution_ui import ConflictResolutionUI
import multiprocessing
import time
import signal

@pytest.fixture(scope="module")
def server():
    """Fixture to run the Flask server in a separate process"""
    # Start server
    ui = ConflictResolutionUI()
    server_process = multiprocessing.Process(
        target=ui.run,
        kwargs={'host': 'localhost', 'port': 5000}
    )
    server_process.start()
    time.sleep(1)  # Give the server time to start
    
    yield
    
    # Cleanup
    server_process.terminate()
    server_process.join()

@pytest.fixture(autouse=True)
def setup(page: Page, server):
    """Setup for each test"""
    page.goto('http://localhost:5000/conflicts')

def test_resolution_modal(page: Page):
    """Test the resolution modal functionality"""
    # Wait for conflicts to load
    page.wait_for_selector('.list-group-item')
    
    # Click resolve button on first conflict
    page.click('button:text("Resolve")')
    
    # Verify modal appears
    modal = page.locator('.modal')
    expect(modal).to_be_visible()
    
    # Verify resolution options are loaded
    expect(page.locator('#resolutionOptions')).to_be_visible()
    
    # Select first resolution option
    page.click('.form-check-input')
    
    # Verify impact analysis appears
    expect(page.locator('#impactAnalysis')).to_be_visible()
    expect(page.locator('#impactAnalysis')).to_contain_text('Impact Analysis')
    
    # Close modal
    page.click('button:text("Cancel")')
    expect(modal).to_be_hidden()

def test_impact_analysis_update(page: Page):
    """Test that impact analysis updates when selecting different resolutions"""
    # Open resolution modal
    page.click('button:text("Resolve")')
    
    # Get all resolution options
    options = page.locator('.form-check-input').all()
    
    if len(options) > 1:
        # Select first option and store impact
        options[0].click()
        first_impact = page.locator('#impactAnalysis').inner_text()
        
        # Select second option and verify impact changes
        options[1].click()
        second_impact = page.locator('#impactAnalysis').inner_text()
        assert first_impact != second_impact

def test_apply_resolution(page: Page):
    """Test applying a resolution"""
    # Open resolution modal
    page.click('button:text("Resolve")')
    
    # Select first resolution
    page.click('.form-check-input')
    
    # Click apply
    with page.expect_navigation():
        page.click('button:text("Apply Resolution")')
    
    # Verify we're back on conflicts page
    expect(page).to_have_url('http://localhost:5000/conflicts')

def test_history_filters(page: Page):
    """Test history page filters"""
    # Navigate to history page
    page.click('a:text("History")')
    
    # Set date range
    page.fill('#startDate', '2024-01-01')
    page.fill('#endDate', '2024-12-31')
    
    # Select conflict type
    page.select_option('#conflictType', 'GENDER_REQUIREMENT')
    
    # Select resolution type
    page.select_option('#resolutionType', 'SWAP_STAFF')
    
    # Apply filters
    with page.expect_navigation():
        page.click('button:text("Apply Filters")')
    
    # Verify URL contains filter parameters
    expect(page).to_have_url(lambda url: 'startDate=2024-01-01' in url)
    expect(page).to_have_url(lambda url: 'endDate=2024-12-31' in url)
    expect(page).to_have_url(lambda url: 'conflictType=GENDER_REQUIREMENT' in url)
    expect(page).to_have_url(lambda url: 'resolutionType=SWAP_STAFF' in url)

def test_conflict_details_navigation(page: Page):
    """Test navigation to conflict details page"""
    # Click view details on first conflict
    with page.expect_navigation():
        page.click('a:text("View Details")')
    
    # Verify we're on details page
    expect(page.locator('.breadcrumb-item.active')).to_have_text('Details')
    
    # Verify content sections are present
    expect(page.locator('h5:text("Affected Components")')).to_be_visible()
    expect(page.locator('h5:text("Conflict Analysis")')).to_be_visible()
    expect(page.locator('h5:text("Suggested Resolutions")')).to_be_visible()

def test_resolution_confirmation(page: Page):
    """Test resolution confirmation dialog"""
    # Open resolution modal
    page.click('button:text("Resolve")')
    
    # Select resolution
    page.click('.form-check-input')
    
    # Mock confirmation dialog
    page.on('dialog', lambda dialog: dialog.accept())
    
    # Click apply and verify navigation
    with page.expect_navigation():
        page.click('button:text("Apply Resolution")')
    
    expect(page).to_have_url('http://localhost:5000/conflicts')

def test_error_handling(page: Page):
    """Test error handling in UI"""
    # Test invalid conflict details
    page.goto('http://localhost:5000/conflicts/invalid-id/details')
    expect(page.locator('text=Conflict not found')).to_be_visible()
    
    # Test failed resolution
    page.goto('http://localhost:5000/conflicts')
    page.click('button:text("Resolve")')
    
    # Mock failed API call
    page.route('/conflicts/*/resolve', lambda route: route.fulfill(
        status=500,
        json={'error': 'Failed to apply resolution'}
    ))
    
    # Try to apply resolution
    page.click('.form-check-input')
    page.click('button:text("Apply Resolution")')
    
    # Verify error message
    expect(page.locator('text=Failed to apply resolution')).to_be_visible()

def test_responsive_design(page: Page):
    """Test responsive design breakpoints"""
    # Test mobile view
    page.set_viewport_size({'width': 375, 'height': 667})
    expect(page.locator('.navbar-collapse')).to_be_hidden()
    
    # Test tablet view
    page.set_viewport_size({'width': 768, 'height': 1024})
    expect(page.locator('.col-md-3')).to_be_visible()
    
    # Test desktop view
    page.set_viewport_size({'width': 1920, 'height': 1080})
    expect(page.locator('.container')).to_have_css('max-width', '1320px')

if __name__ == '__main__':
    pytest.main([__file__]) 