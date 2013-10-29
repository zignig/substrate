function(doc) {
	if(doc.marked){
		emit(doc._id,null)
	}  
}
