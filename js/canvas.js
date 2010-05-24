//
// Copyright 2006 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// TODO(arv): Make sure no private fields are shown/or rename them.
// TODO(arv): Radial gradient
// TODO(arv): Clipping paths
// TODO(arv): Coordsize
// TODO(arv): Painting mode
// TODO(arv): Optimize
// TODO(arv): It looks like we need to modify the lineWidth slightly

function G_VmlCanvasManager() {
  this.init();
}

G_VmlCanvasManager.prototype = {
  init: function (opt_doc) {
    var doc = opt_doc || document;
    if (/MSIE/.test(navigator.userAgent) && !window.opera) {
      var self = this;
      doc.attachEvent("onreadystatechange", function () {
        self.init_(doc);
      });
    }
  },

  init_: function (doc, e) {
    if (doc.readyState == "complete") {
      // create xmlns
      if (!doc.namespaces["g_vml_"]) {
        doc.namespaces.add("g_vml_", "urn:schemas-microsoft-com:vml");
      }

      // setup default css
      var ss = doc.createStyleSheet();
      ss.cssText = "canvas{display:inline-block; overflow:hidden; text-align:left;}" +
          "canvas *{behavior:url(#default#VML)}";

      // find all canvas elements
      var els = doc.getElementsByTagName("canvas");
      for (var i = 0; i < els.length; i++) {
        if (!els[i].getContext) {
          this.initElement(els[i]);
        }
      }
    }
  },

  fixElement_: function (el) {
    // in IE before version 5.5 we would need to add HTML: to the tag name
    // but we do not care about IE before version 6
    var outerHTML = el.outerHTML;
    var newEl = document.createElement(outerHTML);
    // if the tag is still open IE has created the children as siblings and
    // it has also created a tag with the name "/FOO"
    if (outerHTML.slice(-2) != "/>") {
      var tagName = "/" + el.tagName;
      var ns;
      // remove content
      while ((ns = el.nextSibling) && ns.tagName != tagName) {
        ns.removeNode();
      }
      // remove the incorrect closing tag
      if (ns) {
        ns.removeNode();
      }
    }
    el.parentNode.replaceChild(newEl, el);
    return newEl;
  },

  initElement: function (el) {
    el = this.fixElement_(el);
    el.getContext = function () {
      if (this._context) {
        return this._context;
      }
      return this._context = new G_VmlCanvas(this);
    };

    var self = this; //bind
    el.attachEvent("onpropertychange", function (e) {
      // we need to watch changes to width and height
      switch (e.propertyName) {
        case "width":
        case "height":
          // coord size changed?
          break;
      }
    });

    // if style.height is set

    var attrs = el.attributes;
    if (attrs.width && attrs.width.specified) {
      // TODO: use runtimeStyle and coordsize
      // el.getContext().setWidth_(attrs.width.nodeValue);
      el.style.width = attrs.width.nodeValue + "px";
    }
    if (attrs.height && attrs.height.specified) {
      // TODO: use runtimeStyle and coordsize
      // el.getContext().setHeight_(attrs.height.nodeValue);
      el.style.height = attrs.height.nodeValue + "px";
    }
    //el.getContext().setCoordsize_()
  }
};

var G_vmlCanvasManager = new G_VmlCanvasManager;


function G_VmlCanvas(surface) {
  this.m = G_VmlCanvas.MatrixIdentity();
  this.element = surface;

  this.mStack = [];
  this.aStack = [];
  this.currentPath = [];

  // Canvas context properties
  this.strokeStyle = "#000";
  this.fillStyle = "#ccc";

  this.lineWidth = 1;
  this.lineJoin = 'miter';
  this.lineCap = 'butt';
  this.miterLimit = 10.0;
  this.globalAlpha = 1.0;
};

G_VmlCanvas.dec2hex = [];
(function () {
  for (var i = 0; i < 16; i++) {
    for (var j = 0; j < 16; j++) {
      G_VmlCanvas.dec2hex[i * 16 + j] = i.toString(16) + j.toString(16);
    }
  }
})();

G_VmlCanvas.MatrixIdentity = function() {
  return [
    [1,0,0],
    [0,1,0],
    [0,0,1]
  ];
}

G_VmlCanvas.MatrixMultiply = function(m1, m2) {
  var result = G_VmlCanvas.MatrixIdentity();


  for (var x = 0; x < 3; x++) {
    for (var y = 0; y < 3; y++) {
      var sum = 0;

      for (var z = 0; z < 3; z++) {
        sum += m1[x][z] * m2[z][y];
      }

      result[x][y] = sum;
    }
  }
  return result;
}

G_VmlCanvas.CopyState = function(o1, o2) {
  o2.fillStyle     = o1.fillStyle;
  o2.lineCap       = o1.lineCap;
  o2.lineJoin      = o1.lineJoin;
  o2.lineWidth     = o1.lineWidth;
  o2.miterLimit    = o1.miterLimit;
  o2.shadowBlur    = o1.shadowBlur;
  o2.shadowColor   = o1.shadowColor;
  o2.shadowOffsetX = o1.shadowOffsetX;
  o2.shadowOffsetY = o1.shadowOffsetY;
  o2.strokeStyle   = o1.strokeStyle;
};

G_VmlCanvas.ProcessStyle = function(styleString) {
  var str, alpha = 1.0;

  styleString = String(styleString);
  if (styleString.substring(0, 3) == "rgb") {
    var start = styleString.indexOf("(", 3);
    var end = styleString.indexOf(")", start + 1);
    var guts = styleString.substring(start + 1, end).split(",");

    str = "#";
    for (var i = 0; i < 3; i++) {
      str += G_VmlCanvas.dec2hex[parseInt(guts[i])];
    }

    if ((guts.length == 4) && (styleString.substr(3, 1) == "a")) {
      alpha = guts[3];
    }
  } else {
    str = styleString;
  }

  return [str, alpha];
}

G_VmlCanvas.ProcessLineCap = function(lineCap) {
  switch (lineCap) {
    case 'butt': return 'flat';
    case 'round': return 'round';
    case 'square': return 'square';
  }
};

G_VmlCanvas.prototype.clearRect = function() {
  this.element.innerHTML = "";
  this.currentPath = [];
};

G_VmlCanvas.prototype.beginPath = function() {
  // TODO(glen): Branch current matrix so that save/restore has no effect
  //             as per safari docs.

  this.currentPath = [];
};

G_VmlCanvas.prototype.moveTo = function(aX, aY) {
  this.currentPath.push({type: 'moveTo', x: aX, y:aY});
};

G_VmlCanvas.prototype.lineTo = function(aX, aY) {
  this.currentPath.push({type: 'lineTo', x: aX, y:aY});
};

G_VmlCanvas.prototype.bezierCurveTo = function(aCP1x, aCP1y, aCP2x, aCP2y, aX, aY) {
  this.currentPath.push({type: 'bezierCurveTo',
                         cp1x: aCP1x,
                         cp1y: aCP1y,
                         cp2x: aCP2x,
                         cp2y: aCP2y,
                         x: aX,
                         y: aY});
}

G_VmlCanvas.prototype.quadraticCurveTo = function(aCPx, aCPy, aX, aY) {
  // VML's qb produces different output to Firefox's
  this.bezierCurveTo(aCPx, aCPy, aCPx, aCPy, aX, aY);
}

G_VmlCanvas.prototype.arc = function(aX, aY, aRadius, aStartAngle, aEndAngle, aClockwise) {

  if (!aClockwise) {
    var t = aStartAngle;
    aStartAngle = aEndAngle;
    aEndAngle = t;
  }

  var xStart = aX + (Math.cos(aStartAngle) * aRadius);
  var yStart = aY + (Math.sin(aStartAngle) * aRadius);

  var xEnd = aX + (Math.cos(aEndAngle) * aRadius);
  var yEnd = aY + (Math.sin(aEndAngle) * aRadius);

  this.currentPath.push({type: 'arc',
                         x: aX,
                         y: aY,
                         radius: aRadius,
                         xStart: xStart,
                         yStart: yStart,
                         xEnd: xEnd,
                         yEnd: yEnd});

}

G_VmlCanvas.prototype.strokeRect = function(aX, aY, aWidth, aHeight) {
  // Will destroy any existing path (same as FF behaviour)
  this.beginPath();
  this.moveTo(aX, aY);
  this.lineTo(aX + aWidth, aY);
  this.lineTo(aX + aWidth, aY + aHeight);
  this.lineTo(aX, aY + aHeight);
  this.closePath();
  this.stroke();
}

G_VmlCanvas.prototype.fillRect = function(aX, aY, aWidth, aHeight) {
  // Will destroy any existing path (same as FF behaviour)
  this.beginPath();
  this.moveTo(aX, aY);
  this.lineTo(aX + aWidth, aY);
  this.lineTo(aX + aWidth, aY + aHeight);
  this.lineTo(aX, aY + aHeight);
  this.closePath();
  this.fill();
}

// Gradient / Pattern Stubs
function G_VmlGradient(aType) {
  this.type = aType;
  this.radius1 = 0;
  this.radius2 = 0;
  this.colors = [];
  this.focus = {x: 0, y:0};
}

G_VmlGradient.prototype.addColorStop = function(aOffset, aColor) {
  aColor = G_VmlCanvas.ProcessStyle(aColor);
  this.colors.push({offset: 1-aOffset, color: aColor});
}

G_VmlCanvas.prototype.createLinearGradient = function(aX0, aY0, aX1, aY1) {
  var gradient = new G_VmlGradient("gradient");
  return gradient;
}

G_VmlCanvas.prototype.createRadialGradient = function(aX0, aY0, aR0, aX1, aY1, aR1) {
  var gradient = new G_VmlGradient("gradientradial");
  gradient.radius1 = aR0;
  gradient.radius2 = aR1;
  gradient.focus.x = aX0;
  gradient.focus.y = aY0;
  return gradient;
}

G_VmlCanvas.prototype.drawImage = function (image, var_args) {
  var dx, dy, dw, dh, sx, sy, sw, sh;
  var w = image.width;
  var h = image.height;

  if (arguments.length == 3) {
    dx = arguments[1];
    dy = arguments[2];
    sx = sy = 0;
    sw = dw = w;
    sh = dh = h;
  } else if (arguments.length == 5) {
    dx = arguments[1];
    dy = arguments[2];
    dw = arguments[3];
    dh = arguments[4];
    sx = sy = 0;
    sw = w;
    sh = h;
  } else if (arguments.length == 9) {
    sx = arguments[1];
    sy = arguments[2];
    sw = arguments[3];
    sh = arguments[4];
    dx = arguments[5];
    dy = arguments[6];
    dw = arguments[7];
    dh = arguments[8];
  } else {
    throw "Invalid number of arguments";
  }

  var d = this.Coords(dx, dy);

  var w2 = (sw / 2);
  var h2 = (sh / 2);

  var vmlStr = [];

  // For some reason that I've now forgotten, using divs didn't work
  vmlStr.push(' <g_vml_:group',
              ' coordsize="100,100"',
              ' coordorigin="0, 0"' ,
              ' style="width:100px; height:100px; position:absolute; ');

  // If filters are necessary (rotation exists), create them
  // filters are bog-slow, so only create them if abbsolutely necessary
  // The following check doesn't account for skews (which don't exist
  // in the canvas spec (yet) anyway.

  if (this.m[0][0] != 1 || this.m[0][1]) {
    var filter = [];

    // Note the 12/21 reversal
    filter.push("M11='",this.m[0][0],"',",
                "M12='",this.m[1][0],"',",
                "M21='",this.m[0][1],"',",
                "M22='",this.m[1][1],"',",
                "Dx='",d.x,"',",
                "Dy='",d.y,"'");

    // Bounding box calculation (need to minimize displayed area so that filters
    // don't waste time on unused pixels.
    var max = d;
    var c2 = this.Coords(dx+dw, dy);
    var c3 = this.Coords(dx, dy+dh);
    var c4 = this.Coords(dx+dw, dy+dh);

    max.x = Math.max(max.x, c2.x, c3.x, c4.x);
    max.y = Math.max(max.y, c2.y, c3.y, c4.y);

    vmlStr.push(' padding:0px ', Math.floor(max.x), 'px ', Math.floor(max.y),
                'px 0px;filter:progid:DXImageTransform.Microsoft.Matrix(',
                filter.join(""), ', sizingmethod=\'clip\');')
  } else {
    vmlStr.push(' top:',d.y,'px; left:',d.x,'px;')
  }

  vmlStr.push(' ">' ,
              '<g_vml_:image src="', image.src, '"',
              ' style="width:', dw, ';',
              ' height:', dh, ';"',
              ' cropleft="', sx / w, '"',
              ' croptop="', sy / h, '"',
              ' cropright="', (w - sx - sw) / w, '"',
              ' cropbottom="', (h - sy - sh) / h, '"',
              ' />',
              ' </g_vml_:group>');

  //this.element.innerHTML += vmlStr.join("");
  this.element.insertAdjacentHTML("BeforeEnd",
                                  vmlStr.join(""));
};

G_VmlCanvas.prototype.stroke = function(aFill) {
  var strokeColor, fillColor, opacity;
  var lineStr = [];
  var lineOpen = false;

  if (aFill) {
    var a = G_VmlCanvas.ProcessStyle(this.fillStyle);
    fillColor = a[0];
    opacity = a[1] * this.globalAlpha;
  } else {
    var a = G_VmlCanvas.ProcessStyle(this.strokeStyle);
    strokeColor = a[0];
    opacity = a[1] * this.globalAlpha;
  }

  lineStr.push('<g_vml_:shape',
               ' fillcolor="', fillColor, '"',
               ' filled="',(aFill) ? "true" : "false",'"',
               ' style="position:absolute; width:10; height:10;"',
               ' coordorigin="0 0" coordsize="10 10"',
               ' stroked="',(aFill) ? "false" : "true",'"',
               ' strokeweight="', this.lineWidth, '"',
               ' strokecolor="', strokeColor, '"',
               ' path="');

  var newSeq = false;
  var min = {x:null, y:null};
  var max = {x:null, y:null};

  for (var i = 0; i < this.currentPath.length; i++) {
    var p = this.currentPath[i];

    if (p.type == 'moveTo') {
      lineStr.push(' m ');
      var c = this.Coords(p.x, p.y);
      lineStr.push(Math.floor(c.x), ',', Math.floor(c.y));
    } else if (p.type == 'lineTo') {
      lineStr.push(' l ');
      var c = this.Coords(p.x, p.y);
      lineStr.push(Math.floor(c.x), ',', Math.floor(c.y));
    } else if (p.type == 'close') {
      lineStr.push(' x ');
    } else if (p.type == 'bezierCurveTo') {
      lineStr.push(' c ');
      var c = this.Coords(p.x, p.y);
      var c1 = this.Coords(p.cp1x, p.cp1y);
      var c2 = this.Coords(p.cp2x, p.cp2y);
      lineStr.push(Math.floor(c1.x), ',', Math.floor(c1.y), ',',
                   Math.floor(c2.x), ',', Math.floor(c2.y), ',',
                   Math.floor(c.x), ',', Math.floor(c.y));
    } else if (p.type == 'arc') {
      lineStr.push(' ar ');
      var c  = this.Coords(p.x, p.y);
      var cStart = this.Coords(p.xStart, p.yStart);
      var cEnd = this.Coords(p.xEnd, p.yEnd);

      // TODO(glen): FIX (matricies (scale+rotation) now buggered this up)
      //             VML arc also doesn't seem able to do rotated non-circular
      //             arcs without parent grouping.
      var absXScale = this.m[0][0];
      var absYScale = this.m[1][1];

      lineStr.push(Math.floor(c.x - absXScale * p.radius), ',', Math.floor(c.y - absYScale * p.radius), ' ',
                   Math.floor(c.x + absXScale * p.radius), ',', Math.floor(c.y + absYScale * p.radius), ' ',
                   Math.floor(cStart.x), ',', Math.floor(cStart.y), ' ',
                   Math.floor(cEnd.x), ',', Math.floor(cEnd.y));
    }


    // TODO(glen): Following is broken for curves due to
    //             move to proper paths.

    // Figure out dimensions so we can do gradient fills
    // properly
    if (min.x == null || c.x < min.x) {
      min.x = c.x;
    }
    if (max.x == null || c.x > max.x) {
      max.x = c.x;
    }
    if (min.y == null || c.y < min.y) {
      min.y = c.y;
    }
    if (max.y == null || c.y > max.y) {
      max.y = c.y;
    }
  }
  lineStr.push(' ">');

  if (typeof this.fillStyle == 'object') {
    var focus = {x:"50%", y:"50%"};
    var width = (max.x - min.x);
    var height = (max.y - min.y);
    var dimension = (width > height) ? width : height;

    focus.x = Math.floor((this.fillStyle.focus.x / width) * 100 + 50) + '%';
    focus.y = Math.floor((this.fillStyle.focus.y / height) * 100 + 50) + '%';

    var colors = [];

    // inside radius (%)
    if (this.fillStyle.type == 'gradientradial') {
      var inside = (this.fillStyle.radius1 / dimension * 100);

      // percentage that outside radius exceeds inside radius
      var expansion = (this.fillStyle.radius2 / dimension * 100) - inside;
    } else {
      var inside = 0;
      var expansion = 100;
    }

    var insidecolor = {offset:null, color:null};
    var outsidecolor = {offset:null, color:null};

    // We need to sort 'colors' by percentage, from 0 > 100 otherwise ie won't
    // interpret it correctly
    this.fillStyle.colors.sort(function (cs1, cs2) {
      return cs1.offset - cs2.offset;
    });

    for (var i = 0; i < this.fillStyle.colors.length; i++) {
      var fs = this.fillStyle.colors[i];

      colors.push( (fs.offset * expansion) + inside,'% ',fs.color,",");

      if (fs.offset > insidecolor.offset || insidecolor.offset == null) {
        insidecolor.offset = fs.offset;
        insidecolor.color = fs.color;
      }

      if (fs.offset < outsidecolor.offset || outsidecolor.offset == null) {
        outsidecolor.offset = fs.offset;
        outsidecolor.color = fs.color;
      }
    }
    colors.pop();

    lineStr.push('<g_vml_:fill',
                 ' color="',outsidecolor.color,'"',
                 ' color2="',insidecolor.color,'"',
                 ' type="', this.fillStyle.type, '"',
                 ' focusposition="', focus.x, ', ', focus.y, '"',
                 ' colors="', colors.join(''), '" />');
  }

  if (aFill) {
    lineStr.push('<g_vml_:fill opacity="', opacity, '" />');
  } else {
    lineStr.push('<g_vml_:stroke opacity="', opacity, '" joinstyle="', this.lineJoin, '" miterlimit="', this.miterLimit, '" endcap="', G_VmlCanvas.ProcessLineCap(this.lineCap) ,'" />');
  }

  lineStr.push('</g_vml_:shape>');

  this.element.insertAdjacentHTML("beforeEnd", lineStr.join(""));

  this.currentPath = [];
};

G_VmlCanvas.prototype.fill = function() {
  this.stroke(true);
}

G_VmlCanvas.prototype.closePath = function() {
  this.currentPath.push({type: 'close'});
};

G_VmlCanvas.prototype.Coords = function(aX, aY) {
  return {
    x: (aX * this.m[0][0] + aY * this.m[1][0] + this.m[2][0]),
    y: (aX * this.m[0][1] + aY * this.m[1][1] + this.m[2][1])
  }
};

G_VmlCanvas.prototype.save = function() {
  var o = {};
  G_VmlCanvas.CopyState(this, o);
  this.aStack.push(o);
  this.mStack.push(this.m);
  this.m = G_VmlCanvas.MatrixMultiply(G_VmlCanvas.MatrixIdentity(), this.m);//new G_VmlCanvas.Matrix(this.m.x, this.m.y, this.m.rot, this.m.xScale, this.m.yScale);
};

G_VmlCanvas.prototype.restore = function() {
  G_VmlCanvas.CopyState(this.aStack.pop(), this);
  this.m = this.mStack.pop();
};

G_VmlCanvas.prototype.translate = function(aX, aY) {
  var m1 = [
    [1,  0,  0],
    [0,  1,  0],
    [aX, aY, 1]
  ];

  this.m = G_VmlCanvas.MatrixMultiply(m1, this.m);
};

G_VmlCanvas.prototype.rotate = function(aRot) {
  var c = Math.cos(aRot);
  var s = Math.sin(aRot);

  var m1 = [
    [c,  s, 0],
    [-s, c, 0],
    [0,  0, 1]
  ];

  this.m = G_VmlCanvas.MatrixMultiply(m1, this.m);
};

G_VmlCanvas.prototype.scale = function(aX, aY) {
  var m1 = [
    [aX, 0,  0],
    [0,  aY, 0],
    [0,  0,  1]
  ];

  this.m = G_VmlCanvas.MatrixMultiply(m1, this.m);
};


/******** STUBS ********/
G_VmlCanvas.prototype.clip = function() {;}
G_VmlCanvas.prototype.createPattern = function() {;}

