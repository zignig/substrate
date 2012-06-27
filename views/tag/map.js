function(doc) {
    if (!doc.tags) {
        return;
    }
    for (var i = 0; i < doc.tags.length; ++i) {
        emit(doc.tags[i],1);
    }
}
