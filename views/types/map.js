function(doc) {
if(doc.status == 0){
 if(doc._attachments){
  for( var idx in doc._attachments){
   emit(idx.split(".")[1],1);
} 
 }
}
}
