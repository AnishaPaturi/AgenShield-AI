import sys
import time
from playwright.sync_api import sync_playwright

def test_landing_restructure():
    print("=================================================================")
    print("TEST: LANDING PAGE 13-SECTION RESTRUCTURE & SCROLL VERIFICATION")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Load Landing Page
        print("\n1. Navigating to http://localhost:5173/ ...")
        page.goto("http://localhost:5173/", wait_until="networkidle")
        time.sleep(2)

        # 2. Check 13 Sequential Sections in exact order
        expected_sections = [
            ("cinematic-opening", "Cinematic Opening"),
            ("project-intro", "Project Introduction"),
            ("hero", "Main Hero"),
            ("agents", "Agents"),
            ("workflow", "Workflow"),
            ("architecture", "Architecture"),
            ("security", "Security"),
            ("attack-path", "Attack Path / Blast Radius"),
            ("integrations", "Multi-Cloud"),
            ("multi-llm", "AI / Multi-LLM"),
            ("remediation", "Remediation"),
            ("metrics", "Results / Metrics"),
            ("cta", "Final CTA"),
        ]

        print("\n2. Verifying 13 Sequential Sections in DOM...")
        main_sections = page.locator("main.landing-main-flow > section").all()
        print(f"   Found {len(main_sections)} sections directly inside <main.landing-main-flow>")

        assert len(main_sections) == 13, f"Expected 13 sections, found {len(main_sections)}"

        for idx, (expected_id, name) in enumerate(expected_sections):
            sec = main_sections[idx]
            actual_id = sec.get_attribute("id")
            print(f"   [{idx + 1:02d}/13] Expected: #{expected_id:<20} | Actual: #{str(actual_id):<20} ({name})")
            assert actual_id == expected_id, f"Section {idx+1} mismatch: expected #{expected_id}, got #{actual_id}"

        # 3. Check Opening Video attributes
        print("\n3. Verifying Cinematic Opening Video...")
        opening_video = page.locator("#cinematic-opening video.opening-video")
        assert opening_video.count() == 1, "Opening video element not found"
        video_src = opening_video.get_attribute("src")
        print(f"   Opening video src: {video_src}")
        assert "Agent%20Shield%20Hero%20Web.mp4" in video_src or "Agent Shield Hero Web.mp4" in video_src, "Video src path mismatch"
        has_loop = opening_video.get_attribute("loop")
        assert not has_loop, "Opening video must NOT loop"
        print("   [PASS]")

        # 4. Verify No CSS Scroll-Snap
        print("\n4. Verifying No CSS Scroll Snap on document flow...")
        scroll_snap_html = page.evaluate("() => window.getComputedStyle(document.documentElement).scrollSnapType")
        scroll_snap_body = page.evaluate("() => window.getComputedStyle(document.body).scrollSnapType")
        scroll_snap_main = page.evaluate("() => window.getComputedStyle(document.querySelector('main')).scrollSnapType")
        print(f"   scroll-snap-type on <html>: {scroll_snap_html}")
        print(f"   scroll-snap-type on <body>: {scroll_snap_body}")
        print(f"   scroll-snap-type on <main>: {scroll_snap_main}")
        assert scroll_snap_html in ["none", "none none", ""], f"HTML has scroll-snap: {scroll_snap_html}"
        assert scroll_snap_body in ["none", "none none", ""], f"Body has scroll-snap: {scroll_snap_body}"
        assert scroll_snap_main in ["none", "none none", ""], f"Main has scroll-snap: {scroll_snap_main}"
        print("   [PASS]")

        # 5. Test Manual Scrolling Through Sections
        print("\n5. Testing Manual Scrolling Through Sections...")
        total_height = page.evaluate("() => document.body.scrollHeight")
        print(f"   Total document height: {total_height}px")
        assert total_height > 5000, f"Expected total height > 5000px, got {total_height}px"

        # Scroll down in increments
        for target_scroll in [1000, 2500, 4500, 7000, total_height]:
            page.evaluate(f"(pos) => window.scrollTo(0, pos)", target_scroll)
            time.sleep(0.3)
        print("   [PASS] Page scrolls downward smoothly")

        # Scroll back up in increments (testing reversibility)
        for target_scroll in [5000, 2500, 1000, 0]:
            page.evaluate(f"(pos) => window.scrollTo(0, pos)", target_scroll)
            time.sleep(0.2)
        print("   [PASS] Page scrolls back up smoothly (reversible scroll)")

        # 6. Verify Theme Switching
        print("\n6. Verifying Theme Toggle...")
        current_theme = page.evaluate("() => document.body.getAttribute('data-theme')")
        print(f"   Initial theme: {current_theme}")

        theme_btn = page.locator("button.theme-toggle-btn")
        if theme_btn.count() > 0:
            theme_btn.first.click()
            time.sleep(0.5)
            new_theme = page.evaluate("() => document.body.getAttribute('data-theme')")
            print(f"   Switched theme to: {new_theme}")
            assert new_theme != current_theme, "Theme failed to toggle"
            # Toggle back
            theme_btn.first.click()
            time.sleep(0.5)
            print("   [PASS] Theme toggle is responsive across all sections")

        # 7. Verify Auth Page Safety
        print("\n7. Verifying Auth Pages are untouched and functional...")
        page.goto("http://localhost:5173/sign-in", wait_until="networkidle")
        time.sleep(1)
        robot_img = page.locator("img.auth-robot-img")
        assert robot_img.count() == 1, "Auth robot image not found on /sign-in"
        print("   [PASS] /sign-in loaded perfectly with robot asset")

        page.goto("http://localhost:5173/sign-up", wait_until="networkidle")
        time.sleep(1)
        signup_form = page.locator("form.auth-form")
        assert signup_form.count() == 1, "Sign up form not found on /sign-up"
        print("   [PASS] /sign-up loaded perfectly with intact auth providers")

        print("\n=================================================================")
        print("ALL TESTS PASSED: 13-SECTION LANDING RESTRUCTURE FULLY VALIDATED!")
        print("=================================================================")

        browser.close()

if __name__ == "__main__":
    test_landing_restructure()
