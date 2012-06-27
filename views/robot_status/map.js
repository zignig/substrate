function(doc) {
  if (doc.robot_status === void 0) {
    emit(doc._id,doc);
  }
}
