function(doc) {
	if(doc.name){
		emit(doc._id,doc.name);
	}  
}
