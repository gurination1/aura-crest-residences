import re

with open('/tmp/era_raw.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update CSS links to local files and add Google Fonts fallbacks
head_insert = """
    <link rel="stylesheet" href="/css/dream-heights.css" type="text/css" />
    <link rel="stylesheet" href="/css/lenis.css" type="text/css" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900&family=Italiana&family=Pinyon+Script&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
    <style>
      :root {
        --_fonts---font-display: ambroise-francois-std, "Bodoni Moda", Didot, serif !important;
        --_fonts---font-accent: sloop-script-three, "Pinyon Script", cursive !important;
        --_fonts---font-body: "Maison Neue Extended", "Plus Jakarta Sans", sans-serif !important;
      }
      .preloader_logo .h3, .hero-s_logo .h1 {
        font-family: var(--_fonts---font-display) !important;
      }
      .preloader_logo_a .a2, .hero-s_logo_a .a2 {
        font-family: var(--_fonts---font-accent) !important;
      }
    </style>
"""

# Replace existing CSS links
html = re.sub(r'<link href=\"https://cdn\.prod\.website-files\.com/[^\"]+\.css\"[^>]*>', '', html)
html = re.sub(r'<link rel=\"stylesheet\" href=\"https://unpkg\.com/lenis[^\"]+\.css\">', '', html)

# Insert new head links right before </head>
html = html.replace('</head>', head_insert + '\n</head>')

# 2. Update Image Mappings
image_replacements = [
    # Hero Day
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a25da81dce540a251389928_era-residence_gated-community_day[^\"]*', '/images/dreamsquare.jpg'),
    # Hero Night
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a25da802c253b9e5e3d44f5_era-residence_gated-community_night[^\"]*', '/images/03_gazebo_aerial_opt.jpg'),
    # Preloader BG SVG
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a2311bd477167bbc41c9c03_e22485744735d6f17214f25b6157e9b5_preloader_bg\.svg', '/images/preloader_bg.svg'),
    # Landscape SVG
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a068da7ad91b057365bf974_landscape\.svg', '/images/landscape.svg'),
    # Gallery & Amenity Images
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a150affaf1d8cc969d57dd0_img_cam_02[^\"]*', '/images/01_grand_gate_opt.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a150bbc2a39862be04f2cd5_era-residence-terrace[^\"]*', '/images/04_luxury_living.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a150cc2f810e37eec2ea963_era-residence-garden[^\"]*', '/images/05_poolside.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a0f8c07861fe831459ff0d9_img_cam_05_alpha[^\"]*', '/images/04_dreamsquare_opt.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a15723f346e4b3a6c0af26a_era-residence-terrace[^\"]*', '/images/06_private_theater.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a15185e6803ae588479d12b_era-residence-master-plan[^\"]*', '/images/07_master_plan.png'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a1514d7c27920c70252da1f_era-residence-ground-floor-basement[^\"]*', '/images/slide1_card1.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a1575f46655e8c4e795ec64_era-residence-landscaping[^\"]*', '/images/02_clubhouse_opt.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a15153b797c328a9f2f5964_era-residence-terrace[^\"]*', '/images/slide2_card1.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a1512e5b24991c76981118b_era-residence-gated-community[^\"]*', '/images/dreamcitygate.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a151264dc1dcca76fda17d9_era-residence-pool[^\"]*', '/images/05_poolside.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a1573fc640c344ee0705819_era-residence-parking[^\"]*', '/images/slide3_card1.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a15132fe66907986a254201_era-residence-spa-%26-gym[^\"]*', '/images/02_clubhouse_opt.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a151382fb101ce2ca9db288_era-residence-landscaping[^\"]*', '/images/03_gazebo_aerial_opt.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a1571e51d50c8bcf5f4bb3d_era-residence-garden-2[^\"]*', '/images/slide1_bg.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a1507fddb26e71ff717c30c_img_cam_03[^\"]*', '/images/slide2_bg.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a15080748155bc8e151f5ff_img_cam_07[^\"]*', '/images/slide3_bg.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a150812aefa2e544369d4a6_img_cam_09[^\"]*', '/images/trio_01_dreamsquare.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a0853d5dab31b18f0677081/6a1575180f248400b7124a46_era-residence-kitchen[^\"]*', '/images/trio_02_clubhouse.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a0f8994091fd12c24e79c8a_img_cam_02[^\"]*', '/images/trio_03_gazebo.jpg'),
    (r'https://cdn\.prod\.website-files\.com/6a068da7ad91b057365bf967/6a0f88f3b81e88aabf6874e7_img_cta_1920[^\"]*', '/images/footer_bg.jpg'),
]

for pattern, replacement in image_replacements:
    html = re.sub(pattern, replacement, html)

# Strip srcset attributes on hero images so they don't override the local image with CDN variants
html = re.sub(r'srcset=\"[^\"]*era-residence[^\"]*\"', '', html)

# 3. Clean up external tracking scripts & replace with local JS scripts
html = re.sub(r'<script[^>]*google-analytics[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<script[^>]*googletagmanager[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<script[^>]*gtm\.js.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<noscript>.*?googletagmanager.*?</noscript>', '', html, flags=re.DOTALL)

# Replace Typekit script link
html = re.sub(r'<script[^>]*src=\"https://use\.typekit\.net/pig8glj\.js\"[^>]*></script>', '<script src="/js/typekit.js"></script>', html)

# Replace jQuery script link
html = re.sub(r'<script[^>]*src=\"https://d3e54v103j8qbb\.cloudfront\.net/js/jquery[^\"]+\"[^>]*></script>', '<script src="/js/jquery.min.js"></script>', html)

# Replace Webflow script link
html = re.sub(r'<script[^>]*src=\"https://cdn\.prod\.website-files\.com/[^\"]+/js/webflow[^\"]+\"[^>]*></script>', '<script src="/js/webflow.js"></script>', html)

# Replace GSAP & Plugins
html = re.sub(r'<script[^>]*src=\"https://cdn\.jsdelivr\.net/npm/gsap@3\.15/dist/gsap\.min\.js\"[^>]*></script>', '<script src="/js/gsap.min.js"></script>', html)
html = re.sub(r'<script[^>]*src=\"https://cdn\.jsdelivr\.net/npm/gsap@3\.15/dist/ScrollTrigger\.min\.js\"[^>]*></script>', '<script src="/js/ScrollTrigger.min.js"></script>', html)
html = re.sub(r'<script[^>]*src=\"https://cdn\.jsdelivr\.net/npm/gsap@3\.15/dist/SplitText\.min\.js\"[^>]*></script>', '<script src="/js/SplitText.min.js"></script>', html)
html = re.sub(r'<script[^>]*src=\"https://cdn\.jsdelivr\.net/npm/gsap@3\.15/dist/CustomEase\.min\.js\"[^>]*></script>', '<script src="/js/CustomEase.min.js"></script>', html)
html = re.sub(r'<script[^>]*src=\"https://unpkg\.com/lenis[^\"]+\.min\.js\"[^>]*></script>', '<script src="/js/lenis.min.js"></script>', html)
html = re.sub(r'<script[^>]*src=\"https://cdn\.jsdelivr\.net/npm/lottie-web[^\"]+\.min\.js\"[^>]*></script>', '<script src="/js/lottie.min.js"></script>', html)

# Replace Slater remote loader script at bottom with direct local import
slater_regex = r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', function \(\) \{.*?loadtwc\(src\);\s*\}\);\s*</script>'
html = re.sub(slater_regex, '<script type="module" src="/js/slater.js"></script>', html, flags=re.DOTALL)

# 4. Text and Branding Replacements
# Preloader & Hero branding
html = html.replace('Era<br/>Residence', 'Dream<br/>Heights')
html = html.replace('Era <br/>Residence', 'Dream <br/>Heights')
html = html.replace('Era<br />Residence', 'Dream<br />Heights')
html = html.replace('Era<br>Residence', 'Dream<br>Heights')
html = html.replace('Era Residence', 'Dream Heights')
html = html.replace('ERA Residence', 'Dream Heights')
html = html.replace('ERA Residences', 'Dream Heights Residences')
html = html.replace('Era residences', 'Dream Heights residences')

html = html.replace('Estepona', 'Dharamkot')
html = html.replace('Costa', 'Himalayan')
html = html.replace('del Sol', 'Sanctuary')
html = html.replace('New Golden Mile', 'Dhauladhar Range')
html = html.replace('Spain', 'Himachal')
html = html.replace('Marbella', 'Kangra Valley')
html = html.replace('25 residences', '28 residences')

# Title
html = re.sub(r'<title>.*?</title>', '<title>Dream Heights — Contemporary Himalayan Residences in Dharamkot</title>', html)

with open('/root/dreamheights-source/index.html', 'w', encoding='utf-8') as out:
    out.write(html)

print('✓ Successfully generated /root/dreamheights-source/index.html!')
