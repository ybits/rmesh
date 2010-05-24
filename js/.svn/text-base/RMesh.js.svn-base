var g_rmesh;

function RMesh(element, url) 
{
	//Set simple init stuff
	this.root = $('#' + element);
	this.canvasHeight = 600;
	this.canvasWidth = 600;
	this.data = [];
	this.points = [];
	this.url = url;
	this.stateType = 'pts';
	
	// Process major init stuff
	this.init();
	this.cgalRender = new CgalRenderJson('canvas');
}

RMesh.prototype.init = function() 
{
	// Build the rmesh html structure dynamically
	var table = $('<table>');
	var tr = $('<tr id="rowWrap">');
	tr.append($('<td id="navigation">'));
	tr.append($('<td id="rendering">'));
	table.append(tr);
	$(this.root).append(table);
	
	this.initNavigation();
	this.initRendering();

}

RMesh.prototype.initNavigation = function()
{
	_self = this;
	// Init the navigation section
	$('#navigation').append(this.buildNavigationHtml());
	$('#tabs').tabs();
	$('#tabs').bind('tabsselect', function(event, ui) {

	    // Objects available in the function context:
	    //ui.tab     // anchor element of the selected (clicked) tab
	    //ui.panel   // element, that contains the selected/clicked tab contents
	    //ui.index   // zero-based index of the selected (clicked) tab
	
		

	});
	
	// Attach all the event for the navigation section
	$("#points_rdm3_btn").click(function(event){
	   	_self.addRandomPoints(3);
	});
	
	$("#points_rdm50_btn").click(function(event){
	   	_self.addRandomPoints(50);
	});
	
	$("#points_rdm100_btn").click(function(event){
	   	_self.addRandomPoints(100);
	});
	
	$("#points_compute_btn").click(function(event){
		if (_self.points.length > 2) {
			_self.computeTriangulation();
			_self.renderTriangulation();
		}
	});
	
	$("#points_tri_btn").change(function(event){
		if ($(this).is(":checked")) { 
      		_self.renderTriangulation();
		}
		
	});
	
	$("#points_st_btn").change(function(event){
      	if ($(this).is(":checked")) { 
			_self.renderSpanningTree();
			_self.renderTriangulation(false);
		}
		else {
			_self.renderTriangulation();
		}
	});
	
	$("#points_quad_btn").click(function(event){
      	_self.renderQuadrangulation();
	});

	$("#points_clear_btn").click(function(event){
		_self.clear();
		_self.resetExtendedState();
	});
}

RMesh.prototype.resetExtendedState = function()
{
	$("#points_tri_btn").attr("checked", false);
	$("#points_st_btn").attr("checked", false);
	$("#points_quad_btn").attr("checked", false);
}

RMesh.prototype.buildNavigationHtml = function()
{
	// Return the bulk of the tabs/tab areas
	var h = $('<div id="tabs" style="width: 375px;"> \
		<ul> \
		<li><a href="#fragment-1"><span>Point Set</span></a></li> \
		<li><a href="#fragment-2"><span>Polygon</span></a></li> \
		<li><a href="#fragment-3"><span>About</span></a></li> \
		</ul> \
		<div id="fragment-1"> \
		<div class="group"> \
		<div style="margin-bottom: 10px;"><span id="points_info">Click on the canvas to add points &rarr;</span></div>\
		<div><span>Or use the buttons below:</span></div> \
		<input id="points_rdm3_btn" type="button" value="Add 3" /> \
		<input id="points_rdm50_btn" type="button" value="Add 50"  /> \
		<input id="points_rdm100_btn" type="button" value="Add 100" /> \
		</div> \
		<div class="group"> \
		<input id="points_compute_btn" type="button" value="Compute" /> \
		<input id="points_clear_btn" type="button" value="Clear" /> \
		</div>	\
		<div id="points_extended" class="group"> \
		<div><input type="radio" value="tri" id="points_tri_btn" name="state"> Triangulation</div> \
		<div id="points_st_hid" style="margin-left: 20px;"><input type="checkbox" name="st_cbx" id="points_st_btn"> \
		Spanning Tree</div> \
		<div><input type="radio" value="quad" id="points_quad_btn" name="state"> Quadrangulation</div> \
		</div> \
		<!--div id="points_stat" style=" text-align: left; border: dotted 1px gray; display:none;"> \
		<div> \
		<h2 style="text-align: left;">Statistics</h2> \
		</div> \
		<div id="points_statistics"> \
		</div> \
		</div--> \
		</div> \
		<div id="fragment-2"> \
		Nothing to see here, yet. \
		</div>\
		<div id="fragment-3"> \
		RMesh v2 is a complete rewrite of my <a href="http://www.cs.drexel.edu/~rdb34/rmesh/"> \
		undergraduate research project.</a> \
		This version is web enabled using the following stack: \
		<ul> \
		<li>Apache</li> \
		<li>Python</li> \
		<li>Cgal-python</li> \
		<li>Jquery</li> \
		</ul> \
		</div>\
		</div> <!-- end tabs -->');

 	return h;
}

RMesh.prototype.initRendering = function()
{
	_self = this;
	
	// Build and attach all the rendering html
	$('#rendering').append(this.buildRenderingHtml());
	
	// Attach clicking to canvas
	$('#canvas').click(function(e){
		_self.addPointAt(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top);
	});
	
	// Set up cool loading spinner thing
	$('#loading').hide()
    $('#loading').ajaxStart(function() {
        $(this).show();
		var parent = $(this).parent()
		var pos = $(this).parent().offset();
		var width = $(this).parent().width();
		var myWidth = $(this).width();
		var height = $(this).parent().height();
		var myHeight = $(this).height();
		var left = (width / 2) - (myWidth / 2);
		var top = (height / 2) - (myHeight / 2)
		$(this).css( { "left": (pos.left + left) + "px", "top":pos.top + top + "px" } );
    })
    $('#loading').ajaxStop(function() {
        $(this).hide("slow");
    })
}

RMesh.prototype.buildRenderingHtml = function()
{
	// Return the bulk of the rendering section (canvas, etc) in html
	var h = ('<div id="canvasContainer" class="ui-tabs-panel ui-widget-content ui-corner-bottom"> \
		<canvas id="canvas" width="' + this.canvasWidth + '" height="' + this.canvasHeight + '"></canvas> \
	<div id="loading"> \
	</div> \
	</div> \
	');
	return h;
}

RMesh.prototype.addPointAt = function( x, y )
{
	// Add a single point
	var point = [x, y];
	this.points.push(point);
	this.renderPoints();
}

RMesh.prototype.addRandomPoints = function( n )
{
	// Add n points
	for( var i = 0; i < n; i++ ) {
        var point = [Math.floor(Math.random()* (this.canvasWidth - 20) + 10), 
					Math.floor(Math.random() * (this.canvasHeight - 20) + 10)];
		this.points.push(point);
	}
	this.renderPoints();
}

RMesh.prototype.computeTriangulation = function()
{   
	var _self = this;
	this.cgalRender.clearContext();
    $.ajax({
        url: this.url,
        type: "POST",
        data: {"points": this.points, "type": "points"},
        dataType: "json",
        success: function(data){
			_self.setData(data);
            _self.renderTriangulation(true);		
        }
     });
}

RMesh.prototype.getStateType = function()
{
	return this.stateType;
}

RMesh.prototype.setData = function(data)
{
	this.data[this.getStateType()] = data;
}

RMesh.prototype.getData = function()
{
	return this.data[this.getStateType()];
}

RMesh.prototype.renderPoints = function(clear)
{
	var data = [];
	data['points'] = this.points;
	this.cgalRender.renderPoints(data);
	if( clear == undefined ) clear = true; 
	if (clear) $("#points_st_btn").attr("checked", false);
	$("#points_extended").hide("slow");
}

RMesh.prototype.renderTriangulation = function(clear)
{
	if( clear == undefined ) clear = true; 
	this.cgalRender.renderTriangulation(this.getData(), clear);
	$("#points_extended").show("slow");
	$("#points_st_hid").show("slow");
	$("#points_tri_btn").attr("checked", true);
	$("#points_extended").show("slow");
	$("#points_stat").show("slow");
}

RMesh.prototype.renderSpanningTree = function(clear)
{
	this.cgalRender.renderSpanningTree(this.getData(), clear);
	$("#points_extended").show("slow");
	$("#points_stat").show("slow");
}

RMesh.prototype.renderQuadrangulation = function(clear)
{
	this.cgalRender.renderQuadrangulation(this.getData(), clear);
	$("#points_st_hid").hide("slow");
	$("#points_st_btn").attr("checked", false);
	$("#points_extended").show("slow");
	$("#points_stat").show("slow");
}

RMesh.prototype.clear = function()
{
	this.points = [];
	this.data = [];
	$("#points_statistics").empty();
	$("#points_stat").hide("slow");
	$("#points_extended").hide("slow");
	this.cgalRender.clearContext();
}


