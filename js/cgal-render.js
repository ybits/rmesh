function CgalRender(canvas) {
    this.canvas = document.getElementById(canvas);
    this.context = this.getContext();
    this.height = 600;
    this.width = 600;
}    
    
CgalRender.prototype.getContext = function()
{
    var canvas = document.getElementById('canvas');
	if(canvas.getContext )
	{
		var context = canvas.getContext('2d');
        return context;
    }
    return null;
}

CgalRender.prototype.clearContext = function()
{
	this.context.clearRect( 0, 0, this.width, this.height);
}

CgalRender.prototype.renderStructure = function(data)
{
    var context = this.context;
    this.clearContext();
    var _self = this;
    
    $(data).find("vertices").each(function() {
        $(this).find("vertex").each(function() {
            _self.renderVertex(context, $(this));
        });
    });
    
    $(data).find("points").each(function() {
        $(this).find("point").each(function() {
            _self.renderVertex(context, $(this));
        });
    });
    
    $(data).find("edges").each(function() {
        $(this).find("edge").each(function() {
            _self.renderEdge(context, $(this));
        });
    });
    
    $(data).find("faces").each(function() {
        $(this).find("face").each(function() {
            _self.renderFace(context, $(this));
        });
    });
    
    $(data).find("constrained_edges").each(function() {
        $(this).find("edge").each(function() {
            _self.renderEdge(context, $(this));
        });
    });
    
    $(data).find("spanning_tree").each(function() {
        $(this).find("edge").each(function() {
            _self.renderEdge(context, $(this));
        });
    });
    
    $(data).find("circles").each(function() {
        $(this).find("circle").each(function() {
            _self.renderCircle(context, $(this));
        });
    });
    
    $(data).find("holes").each(function() {
        $(this).find("hole").each(function() {
            _self.renderHole(context, $(this));
        });
    });
    
    this.renderStructureExt(data);
 }
 
CgalRender.prototype.renderStructureExt = function(data) {
	// extension
}

 
CgalRender.prototype.renderVertex = function(context, vertex)
{
    context.beginPath();
    context.arc($(vertex).find("xcoord").text(), $(vertex).find("ycoord").text(), 3, 0, Math.PI*2, true );
    context.closePath();
    context.fillStyle = "blue";
    context.fill();
}

CgalRender.prototype.renderEdge = function(context, edge)
{
    context.beginPath();
    var start = true; 
    $(edge).find("point").each(function() {
        if (start) {
            context.moveTo($(this).find("xcoord").text(), $(this).find("ycoord").text());
            start = false;
        }
        else {
            context.lineTo($(this).find("xcoord").text(), $(this).find("ycoord").text());
        }
    });
    context.closePath();
    if ($(edge).attr('type') == 'constrained') {
    	context.strokeStyle= "red";
    }
    else if ($(edge).attr('type') == 'spanning_tree') {
    	context.strokeStyle= "green";
    }
    else {
    	context.strokeStyle= "blue";
    }
    context.stroke();
}

CgalRender.prototype.renderFace = function(context, face)
{
    var _self = this;
    $(face).find("edge").each(function() {
        _self.renderEdge(context, $(this));
    });
} 