function CgalRenderJson(canvas) {
    this.canvas = document.getElementById(canvas);
    this.context = this.getContext();
    this.height = 600;
    this.width = 600;
}    
    
CgalRenderJson.prototype.getContext = function()
{
    var canvas = document.getElementById('canvas');
	if(canvas.getContext )
	{
		var context = canvas.getContext('2d');
        return context;
    }
    return null;
}

CgalRenderJson.prototype.clearContext = function(clear)
{
	if( clear == undefined ) clear = true; 
	if(clear) this.context.clearRect( 0, 0, this.width, this.height);
}

CgalRenderJson.prototype.renderTriangulation = function(data, clear)
{
	this.clearContext(clear);
    var context = this.context;
    var tri = data['triangulation'];	
    
    var faces = tri['faces'];
    for (i in faces) {	
    	this.renderFace(context, faces[i]);
    }

    var points = tri['points'];
    for (i in points) {
    	this.renderPoint(context, points[i]);
    }

 }

CgalRenderJson.prototype.renderQuadrangulation = function(data, clear)
{
	this.clearContext(clear);
    var context = this.context;
	
    var quad = data['quadrangulation'];	
	
    var faces = quad['faces'];
    for (i in faces) {	
    	this.renderFace(context, faces[i]);
    }

	var points = quad['points'];
    for (i in points) {
    	this.renderPoint(context, points[i]);
    }

	var points = quad['steiner_points'];
    for (i in points) {
    	this.renderSteinerPoint(context, points[i]);
    }

	var points = quad['steiner_points2'];
    for (i in points) {
    	this.renderSteinerPoint2(context, points[i]);
    }

	var triangle = quad['triangle'];
	this.renderFinalTriangle(triangle);
	
 }

CgalRenderJson.prototype.renderFinalTriangle = function(triangle)
{
	return true;
}

CgalRenderJson.prototype.renderSpanningTree = function(data, clear)
{
	this.clearContext(clear);
    var context = this.context;
    var tri = data['triangulation'];
    var edges = tri['spanning_tree'];

    for (i in edges) {	
    	this.renderEdge(context, edges[i]);
    }

	var adjacentString = '';
	var counter = 0;
	for (i in edges) {
		for (j in edges[i][0]) {
			point = edges[i][0];
		   	adjacentString += point[j] + ' ';
		}
		adjacentString += '';
	//	context . fillText(' (' + adjacentString + ')', point[0], point[1]);
		context . fillText(counter++, point[0], point[1]);
	}

 }


CgalRenderJson.prototype.renderPoints = function(data, clear)
{
	this.clearContext(clear);
	var context = this.context;
    var points = data['points'];

    for (i in points) {	
    	this.renderPoint(context, points[i]);
    }
}

CgalRenderJson.prototype.renderSteinerPoints = function(data, clear)
{
	this.clearContext(clear);
	var context = this.context;
    var points = data['steiner_points'];

    for (i in points) {	
    	this.renderSteinerPoint(context, points[i]);
    }
}
 
CgalRenderJson.prototype.renderStructureExt = function(data) {
	// extension
}

 
CgalRenderJson.prototype.renderPoint = function(context, point)
{
	//var randColors = new Array('green', 'red', 'blue', 'purple', 'pink');
	//var randColors = new Array('#660099', '#CC0099', 'green');
	//var randColors  = new Array('purple');
	//var colorIndex = randomnumber=Math.floor(Math.random()*randColors.length);
    context.beginPath();
    context.arc(point[0], point[1], 2, 0, Math.PI*2, true );
    context.closePath();
    context.fillStyle = "red";
	//context.fillStyle = "dark green";
	//context.fillStyle = "purple";
	//context.fillStyle = randColors[colorIndex];
    context.fill();

	/*
 	var adjacentString = '';
	for (j in point) {
	   adjacentString += point[j] + ' ';
	}
	adjacentString += '';
	context . fillText(' (' + adjacentString + ')', point[0], point[1]);
	*/
}

CgalRenderJson.prototype.renderSteinerPoint = function(context, point)
{
    context.beginPath();
    context.arc(point[0], point[1], 2, 0, Math.PI*2, true );
    context.closePath();
    context.fillStyle = "green";
    context.fill();
}

CgalRenderJson.prototype.renderSteinerPoint2 = function(context, point)
{
    context.beginPath();
    context.arc(point[0], point[1], 2, 0, Math.PI*2, true );
    context.closePath();
    context.fillStyle = "yellow";
    context.fill();
}

CgalRenderJson.prototype.renderEdge = function(context, edge)
{
    context.beginPath();
    var start = true; 
    for (i in edge) {
        if (start) {
            context.moveTo(edge[i][0], edge[i][1]);
            start = false;
        }
        else {
            context.lineTo(edge[i][0], edge[i][1]);
        }
    }
    context.closePath();
    context.strokeStyle= "pink";
    context.stroke();
}

CgalRenderJson.prototype.renderTriangle = function(context, triangle)
{
    context.beginPath();
    var start = true; 
    for (i in triangle) {
        if (start) {
            context.moveTo(face[i][0], face[i][1]);
            start = false;
        }
        else {
            context.lineTo(face[i][0], face[i][1]);
        }
    }
    context.closePath();
    context.strokeStyle= "blue";
    context.fill();
}

CgalRenderJson.prototype.renderFace = function(context, face)
{
    context.beginPath();
    var start = true; 
    for (i in face) {
        if (start) {
            context.moveTo(face[i][0], face[i][1]);
            start = false;
        }
        else {
            context.lineTo(face[i][0], face[i][1]);
        }
    }
    context.closePath();
    context.strokeStyle= "blue";
    context.stroke();
} 