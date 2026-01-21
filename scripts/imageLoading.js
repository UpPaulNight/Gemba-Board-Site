// Map of id -> current seqNumber to know what we've already loaded
const currentSequenceNumbers = new Map();

async function loadManifest() {
  // Keep JSON fresh during dev & in production if you want quick propagation
  const res = await fetch("/downloaded_ids.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load JSON: ${res.status}`);

  return res.json();
}

function withSequence(url, seqNumber) {
  const u = new URL(url, window.location.origin);
  u.searchParams.set("v", seqNumber);
  return u.toString();
}

function updateImage(id, url, seqNumber) {
  const imgEl = document.getElementById(`img-${id}`);
  if (!imgEl) return;

  // Only update if the seqNumber changed
  if (currentSequenceNumbers.get(id) === seqNumber) return;

  // Preload into an Image object to avoid flicker and broken states
  const preloader = new Image();
  preloader.decoding = "async";
  preloader.onload = () => {
    // Swap atomically once loaded
    imgEl.src = preloader.src;
    currentSequenceNumbers.set(id, seqNumber);
  };
  preloader.onerror = () => {
    console.error(`Failed to load image for ${id}`, preloader.src);
  };

  preloader.src = withSequence(url, seqNumber);
}

async function refreshImages() {
  try {
    const manifest = await loadManifest();
    for (const item of manifest.images) {
      updateImage(item.id, item.url, item.seqNumber);
    }
  } catch (e) {
    console.error(e);
  }
}

// // Initial load
// refreshImages();

// // Re-check every 30s (tune for your needs, or trigger on a button or SSE)
// setInterval(refreshImages, 30000);
