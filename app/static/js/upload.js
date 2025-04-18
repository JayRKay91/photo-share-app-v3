'use strict';

// If the user enters a new album name, override the select value
document.getElementById('uploadForm').addEventListener('submit', function(e) {
  const newAlbum = document.getElementById('new_album').value.trim();
  if (newAlbum) {
    document.getElementById('album').value = newAlbum;
  }
});
