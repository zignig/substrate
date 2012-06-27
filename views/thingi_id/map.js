function(doc) {
	if(doc.thingi_id){
		emit(doc.thingi_id,1);
	}  
}
