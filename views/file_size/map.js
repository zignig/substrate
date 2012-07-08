function(doc) {
    for (var idx in doc._attachments) {
        emit(doc._attachments[idx].length,idx);
    }
}
