# Sustainability Report

## Tool and Scope
- Tool: Lighthouse CLI (npx lighthouse)
- Test date: 2026-03-07
- Pages tested:
  - Home: http://127.0.0.1:8000/
  - Core feature (Browse): http://127.0.0.1:8000/browse/

## Baseline (Before)
### Home
- Performance: 100
- Accessibility: 94
- Best Practices: 96
- SEO: 90
- Report files:
  - docs/performance/artifacts/home_before.report.html
  - docs/performance/artifacts/home_before.report.json

### Browse
- Performance: 100
- Accessibility: 96
- Best Practices: 96
- SEO: 90
- Report files:
  - docs/performance/artifacts/browse_before.report.html
  - docs/performance/artifacts/browse_before.report.json

## Changes Implemented
1. Moved inline JavaScript to external static files and loaded with defer:
   - core/templates/core/base.html
   - core/static/core/js/nav-dropdown.js
   - core/static/core/js/review-ajax.js
2. Added metadata that improves crawl/readiness and removes default favicon console errors:
   - Added meta description in core/templates/core/base.html
   - Added inline SVG favicon in core/templates/core/base.html
3. Added asynchronous review submission (fetch) to reduce full-page reload for a core interaction:
   - core/templates/core/media_detail.html
   - core/views.py

## After Measurement
### Home
- Performance: 100 (no change)
- Accessibility: 94 (no change)
- Best Practices: 100 (+4)
- SEO: 100 (+10)
- Report files:
  - docs/performance/artifacts/home_after.report.html
  - docs/performance/artifacts/home_after.report.json

### Browse
- Performance: 100 (no change)
- Accessibility: 96 (no change)
- Best Practices: 100 (+4)
- SEO: 100 (+10)
- Report files:
  - docs/performance/artifacts/browse_after.report.html
  - docs/performance/artifacts/browse_after.report.json

## Reflection
The app already had strong runtime performance for the tested pages. The implemented changes did not increase Performance scores because baseline was already maxed, but they improved technical quality signals: SEO completeness and Best Practices. The async review flow also reduces unnecessary full-page reloads for user actions and is better aligned with sustainability goals around efficient client-server interactions.
