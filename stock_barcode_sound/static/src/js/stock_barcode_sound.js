openerp.stock_barcode_sound = function(instance){


    var _t     = instance.web._t;
    var QWeb   = instance.web.qweb;


    instance.stock.PickingEditorWidget.include({

        blink: function(op_id){
            var self = this;
            $('.js_pack_op_line[data-id="'+op_id+'"]').get(0).scrollIntoView();
            this._super(op_id);
            var audio_ok = new Audio('/stock_barcode_sound/static/media/bleep.mp3');
            audio_ok.play();
        },

    });


    instance.stock.PickingMainWidget.include({

        scan: function(ean){ //scans a barcode, sends it to the server, then reload the ui
            var self = this;
            var product_visible_ids = this.picking_editor.get_visible_ids();
            return new instance.web.Model('stock.picking')
                .call('process_barcode_from_ui', [self.picking.id, ean, product_visible_ids])
                .then(function(result){
                    console.log(ean);
                    if (result.filter_loc !== false){
                        //check if we have received a location as answer
                        if (result.filter_loc !== undefined){
                            var modal_loc_hidden = self.$('#js_LocationChooseModal').attr('aria-hidden');
                            if (modal_loc_hidden === "false"){
                                var line = self.$('#js_LocationChooseModal .js_loc_option[data-loc-id='+result.filter_loc_id+']').attr('selected','selected');
                            }
                            else{
                                self.$('.oe_searchbox').val(result.filter_loc);
                                self.on_searchbox(result.filter_loc);
                            }
                        }
                    }
                    if (result.operation_id !== false){
                        self.refresh_ui(self.picking.id).then(function(){
                            return self.picking_editor.blink(result.operation_id);
                        });
                    }
                    if (result.filter_loc === false && result.operation_id === false) {
                        var audio_ok = new Audio('/stock_barcode_sound/static/media/error.mp3');
                        audio_ok.play();
                    }
                });
        },

    });

}