openerp.multi_m2o_text_widget = function(instance){
	
	var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    
    // Form view widget
	instance.web.form.MultiReference = instance.web.form.AbstractField.extend(instance.web.form.ReinitializeFieldMixin, {

		template: "MultiReference",
		
		render_value: function() {
	        var self = this;
	        if (! this.get('value')) {
	        	$('.oe_ul_multi_reference li').remove();
	        }
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
	
	
	
	
	// List view widget (column)
	instance.multi_m2o_text_widget.MultiReferenceList = instance.web.list.Column.extend({

		_format: function (row_data, options) {
	    	var self = this;
	        var value = row_data[this.id].value;
	        if (value) {
	        	var tuples = value.split(";");
	        	var wholelink = "";
        		_.each(tuples, function(tuple) {
        			wholelink += _.template('<a class="oe_form_uri" data-many2one-clickable-model="<%-model%>" data-many2one-clickable-id="<%-resid%>">#</a> ', {
        				model: tuple.split(",")[0], 
        				resid: parseInt(tuple.split(",")[1]),
        			});
        		});
        		return wholelink;
	        }
	        return this._super(row_data, options);
		},
		
	});
	
	instance.web.list.columns.add('field.multi_reference', 'instance.multi_m2o_text_widget.MultiReferenceList');

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
	

	
	
	// Tree view widget
	instance.web.TreeView.include({
		
		getdata: function (id, children_ids) {
	        var self = this;
	        self.dataset.read_ids(children_ids, this.fields_list()).done(function(records) {
	            _(records).each(function (record) {
	                self.records[record.id] = record;
	            });
	            var $curr_node = self.$el.find('#treerow_' + id);
	            var children_rows = QWeb.render('MultiReferenceTreeView.rows', {
	                'records': records,
	                'children_field': self.children_field,
	                'fields_view': self.fields_view.arch.children,
	                'fields': self.fields,
	                'level': $curr_node.data('level') || 0,
	                'render': instance.web.format_value,
	                'color_for': self.color_for,
	                'row_parent_id': id
	            });
	            if ($curr_node.length) {
	                $curr_node.addClass('oe_open');
	                $curr_node.after(children_rows);
	            } else {
	                self.$el.find('tbody').html(children_rows);   
	            }
	            
	            self.$("a[data-index]").each(function() {
	                var elem = $(this);
	                var tuple = elem.attr('data-index');
	                var model_name = tuple.split(",")[0];
	            	var model_obj = new instance.web.Model(model_name);
	            	var res_id = parseInt(tuple.split(",")[1]);
					model_obj.call("name_get",[res_id]).then(function(data) {
						var name = data[0][1];
						elem.text(name);
						// I wasn't able to make 'delegate' or 'click' functions work here. This is very ugly but it works.
						elem.attr('href', instance.session.prefix + '/web#id=' + res_id + '&view_type=form&model=' + model_name);
					});
				});
            });
	    },
	});
	
};
