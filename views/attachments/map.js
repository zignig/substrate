function(doc) {
 if(doc._attachments){
  for( var idx in doc._attachments){
   emit([doc.robot_status,idx.split(".")[1]],[doc._id,idx]);
} 
 }
}
