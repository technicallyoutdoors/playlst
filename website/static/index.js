function deletefavorite(favoriteTitle) {
    fetch('/delete_favorite', {
        method: 'POST', 
        body: JSON.stringify({ favoriteTitle: favoriteTitle})
    }).then((_res) => {
        window.location.href = "/favorites";
    })
}