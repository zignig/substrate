function(doc) {
	if(doc.author){
		emit(doc.author,1);
	}  
}
