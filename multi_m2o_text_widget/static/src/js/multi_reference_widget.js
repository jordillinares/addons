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
	
};