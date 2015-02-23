openerp.multi_m2o_text_widget = function(instance){
	
	var QWeb = instance.web.qweb;
    var _t = instance.web._t;

	instance.multi_m2o_text_widget.MultiReference = instance.web.form.FieldMany2One.extend({
		
		template: "MultiReference",
		
	    render_value: function(no_recurse) {
	        var self = this;
	        if (! this.get("value")) {
	            this.display_string("");
	            return;
	        }
	        var display = this.display_value["" + this.get("value")];
	        if (display) {
	            this.display_string(display);
	            return;
	        }
	        if (! no_recurse) {
	        	self.display_value["" + self.get("value")] = self.get("value");
	        	self.render_value(true);  	
	        }
	    },
    
	    display_string: function(str) {
	        var self = this;
	        if (!this.get("effective_readonly")) {
	            this.$input.val(str.split("\n")[0]);
	            this.current_display = this.$input.val();
	            if (this.is_false()) {
	                this.$('.oe_m2o_cm_button').css({'display':'none'});
	            } else {
	                this.$('.oe_m2o_cm_button').css({'display':'inline'});
	            }
	        } else {
	            var tuples = this.get('value').split(";");
	            _.each(tuples, function(tuple) {
	            	var link = tuple;
	            	var follow = "";
	            	var model_name = tuple.split(",")[0];
	            	var model_obj = new instance.web.Model(model_name);
	            	var res_id = parseInt(tuple.split(",")[1]);
         	       	model_obj.call("name_get",[res_id]).then(function(result) {
					   	account_names = {};
					   	_.each(result, function(el) {
					   		account_names[el[0]] = el[1];
					   	});
					   	var link = account_names[res_id];
					   	var $link = $('a[data-index="' + tuple + '"]')
		                .unbind('click')
		                .html(link);
					   	$link.click(function () {
		                    var context = self.build_context().eval();
		                    model_obj.call('get_formview_action', [res_id, context]).then(function(action){
		                        self.do_action(action);
		                    });
		                    return false;
		                 });	
         	       	});     
	            });
	            
	        }
	    },
        
	});
	
	instance.web.form.widgets.add('multi_reference', 'instance.multi_m2o_text_widget.MultiReference');
	
	
	
	
	
	
	
	
	
	
	
	instance.multi_m2o_text_widget.MultiReferenceList = instance.web.list.Column.extend({

		_jformat: function(cadena) {
			return cadena;
		},
		
//		Muestra en consola el valor del campo. Funciona.
	    _format: function (row_data, options) {
	        var value = row_data[this.id].value;
	        var self = this;
	        if (value) {

//	        	FUNCIONA. NO BORRAR.
//	        	var tuples = value.split(";");
//	        	var wholelink = "";
//        		_.each(tuples, function(tuple) {
//        			wholelink += _.template('<a href="<%-href%>"><%-text%></a> ', {text: tuple.split(",")[0], href: tuple.split(",")[1]});
//        		});
//        		console.warn(wholelink);
//        		return wholelink;

	        	var tuples = value.split(";");
	        	var wholelink = "";
	        	
//	        	var getname = function(model_obj, res_id) {
//    				var def = $.Deferred();
//    				model_obj.call("name_get",[res_id]).then(function(result) {
//	        			account_names = {};
//	        			_.each(result, function(el) {
//	        				account_names[el[0]] = el[1];
//	        			});
//	        			def.resolve(account_names[res_id]);
//	        		});
//    				return def;
//	        	};
//	    		_.each(tuples, function(tuple) {
//	    			var model_name = tuple.split(",")[0];
//	        		var res_id = parseInt(tuple.split(",")[1]);
//	        		var model_obj = new instance.web.Model(model_name);
//	        		wholelink += _.template('<a data-many2one-clickable-model="<%-model%>" data-many2one-clickable-id="<%-resid%>"><%-text%></a> ', {
//	        			model: model_name,
//	        			resid: res_id,
//	        			text: getname(model_obj, res_id).then(function(result){return result;}),
//	        		});
//	    		});
//	    		//No entiendo. Con lo que me ha costado llegar a armar el wholelink que pinta aquí en consola, y luego no lo muestra...
//	    		console.log(wholelink);
//		        return wholelink;
	        	
	        	
	        	
	        	
	        	
//	        	function get_name(model_obj,res_id){
//	        		var def = $.Deferred();
//	        		model_obj.call("name_get",[res_id]).then(function(result) {
//	        			account_names = {};
//	        			_.each(result, function(el) {
//	        				account_names[el[0]] = el[1];
//	        			});
//	        			def.resolve(account_names[res_id]);
//	        		});
//	        		return def.promise();
//	        	}
        		_.each(tuples, function(tuple) {
        			var model_name = tuple.split(",")[0];
	        		var res_id = parseInt(tuple.split(",")[1]);
	        		var model_obj = new instance.web.Model(model_name);
//	        		var textorl = get_name(model_obj, res_id).then(function(message) { console.warn(message);return message;});	        		
	        		wholelink += _.template('<a class="oe_form_uri" data-many2one-clickable-model="<%-model%>" data-many2one-clickable-id="<%-resid%>"><%-text%></a> ', {
	        			model: model_name,
	        			resid: res_id,
	        			text: tuple, // No way. I don't know how to get record name. :(
	        		});

        		});
		        return wholelink;
	        } else {
		        return "";	        	
	        }
	    },

	});

	
	instance.web.ListView.List.include({
		render: function()
		{
			var result = this._super(this, arguments),
			self = this;
			this.$current.delegate('a[data-many2one-clickable-model]',
					'click', function()
					{
				self.view.do_action({
					type: 'ir.actions.act_window',
					res_model: jQuery(this).data('many2one-clickable-model'),
					res_id: jQuery(this).data('many2one-clickable-id'),
					views: [[false, 'form']],
				});
					});
			return result;
		},
	});
	
	instance.web.list.columns.add('field.multi_reference', 'instance.multi_m2o_text_widget.MultiReferenceList');
	
	
	
};