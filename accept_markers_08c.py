import Metashape

chunk = Metashape.app.document.chunk #active chunk
for marker in chunk.markers:
	# if marker.label == 'point 12':
	if not marker.position:
		continue
	point = marker.position
	for camera in [c for c in chunk.cameras if c.transform and c.type == Metashape.Camera.Type.Regular]:
		if camera in marker.projections.keys():
			continue #skip existing projections		             
		x, y = camera.project(point)
		if not(x) or not(y):
			continue
		if (0 <= x < camera.sensor.width) and (0 <= y < camera.sensor.height):
			marker.projections[camera] = Metashape.Marker.Projection(Metashape.Vector([x,y]), False)
print("Script finished")