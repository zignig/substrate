function(doc) {
    if (!doc.thingi_derivative) {
        return;
    }
    for (var i = 0; i < doc.thingi_derivative.length; ++i) {
        emit(doc.thingi_derivative[i],1);
    }
}
