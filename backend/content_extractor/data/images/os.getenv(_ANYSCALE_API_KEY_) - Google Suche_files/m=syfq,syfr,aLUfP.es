this._s=this._s||{};(function(_){var window=this;
try{
_.tvb=function(a){this.Dm=a};
}catch(e){_._DumpException(e)}
try{
var uvb=function(a){_.Nn.call(this,a.La);var b=this;this.window=a.service.window.get();this.wa=this.Dm();this.oa=window.orientation;this.ka=function(){var c=b.Dm(),d=b.CTb()&&Math.abs(window.orientation)===90&&b.oa===-1*window.orientation;b.oa=window.orientation;if(c!==b.wa||d){b.wa=c;d=_.ab(b.Ke);for(var e=d.next();!e.done;e=d.next()){e=e.value;var f=new _.tvb(c);try{e(f)}catch(g){_.ca(g)}}}};this.Ke=new Set;this.window.addEventListener("resize",this.ka);this.CTb()&&this.window.addEventListener("orientationchange",
this.ka)};_.E(uvb,_.Nn);uvb.nb=_.Nn.nb;uvb.Ia=function(){return{service:{window:_.On}}};uvb.prototype.addListener=function(a){this.Ke.add(a)};uvb.prototype.removeListener=function(a){this.Ke.delete(a)};
uvb.prototype.Dm=function(){if(vvb()){var a=_.Cl(this.window);a=new _.il(a.width,Math.round(a.width*this.window.innerHeight/this.window.innerWidth))}else a=this.qc()||(_.la()?vvb():this.window.visualViewport)?_.Cl(this.window):new _.il(this.window.innerWidth,this.window.innerHeight);return a.height<a.width};uvb.prototype.destroy=function(){this.window.removeEventListener("resize",this.ka);this.window.removeEventListener("orientationchange",this.ka)};var vvb=function(){return _.la()&&_.Pe.vI()&&!navigator.userAgent.includes("GSA")};
uvb.prototype.qc=function(){return _.wvb};uvb.prototype.CTb=function(){return"orientation"in window};_.wvb=!1;_.Qn(_.AVa,uvb);
_.wvb=!0;
}catch(e){_._DumpException(e)}
try{
_.y("aLUfP");

_.z();
}catch(e){_._DumpException(e)}
})(this._s);
// Google Inc.
