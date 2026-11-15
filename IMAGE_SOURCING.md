# EXPO. Paris — image sourcing
The weekly GitHub Actions workflow scans official exhibition pages and relevant editorial sources already present in expos.json, looking for Open Graph and page images.
It writes **image-candidates.json** for editorial review. It does **not** republish, download, or automatically display images. This avoids inaccurate exhibition artwork and unauthorized reuse.
Only use an image after verifying (1) the image genuinely represents the current exhibition, (2) its license/permission permits use in EXPO. Paris, (3) credit/attribution requirements, and (4) the URL remains accessible.
To approve, add an explicit image URL, credit, and rights record to the corresponding exhibition entry in expos.json. The app must display only such approved entries.
Run manually from GitHub Actions > Discover exhibition image candidates > Run workflow.
