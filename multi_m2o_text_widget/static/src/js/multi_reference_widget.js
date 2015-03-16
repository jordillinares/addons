openerp.multi_m2o_text_widget = function(instance){
	
	var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    
    // Form widget

	instance.web.form.MultiReference = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {

		template: "MultiReference",
		
		render_value: function() {
	        var self = this;
        	if (this.get('value')) {
        		var tuples = this.get('value').split(";");
        		$('.oe_ul_multi_reference li').remove();
	            _.each(tuples, function(tuple) {
	            	var model_name = tuple.split(",")[0];
	            	var model_obj = new instance.web.Model(model_name);
	            	var res_id = parseInt(tuple.split(",")[1]);
	            	var dataset = new instance.web.DataSetStatic(this, model_name, self.build_context());
	            	self.alive(dataset.name_get([res_id])).done(function(data) {
         	       		var name = data[0][1];
         	       		var $li = $(".oe_ul_multi_reference").append('<li class="oe_form_field oe_form_field_many2one" style="display: inline;"><a href="#" class="oe_form_uri">' + name + '</a></li>');
         	       		$li.find('a').filter(function(index) { return $(this).text() === name; }).click(function () {
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
	
	instance.web.form.widgets.add('multi_reference', 'instance.web.form.MultiReference');
	
	
	
	// Tree widget (column)
	instance.multi_m2o_text_widget.MultiReferenceList = instance.web.list.Column.extend({

		_format: function (row_data, options) {
	    	var self = this;
	        var value = row_data[this.id].value;
	        if (value) {
	        	var tuples = value.split(";");
	        	var wholelink = "";
        		_.each(tuples, function(tuple) {
        			wholelink += _.template('<a data-many2one-clickable-model="<%-model%>" data-many2one-clickable-id="<%-resid%>">#</a> ', {
        				model: tuple.split(",")[0], 
        				resid: parseInt(tuple.split(",")[1]),
        			});
        		});
        		return wholelink;
	        }
	        return this._super(row_data, options);
		},
		
	});
	
	instance.web.ListView.List.include({

		render: function() {
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
		
		render_cell: function (record, column) {
			var result = this._super(record, column);
			if (column.widget && column.widget === 'multi_reference') {
				value = record.get(column.id);
				if (value) {					
					var tuples = value.split(";");
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
							$('a[data-many2one-clickable-model="' + model_name + '"][data-many2one-clickable-id="' + res_id + '"]').text(link);
						});     
					});
				}
			}
			return result;
		},
		
	});
	
	instance.web.list.columns.add('field.multi_reference', 'instance.multi_m2o_text_widget.MultiReferenceList');
	
};
