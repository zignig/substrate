function(doc) {
 if(doc._attachments){
  for( var idx in doc._attachments){
   emit(idx,1);
} 
 }
}
