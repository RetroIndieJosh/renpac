init 999 python:
    config.keymap.clear()
    renpy.clear_keymap_cache()
    #$ config.keymap = dict(
        # universal
        #rollback = [ 'K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK', 'mousedown_4' ],
        #screenshot = [ 's', 'alt_K_s', 'alt_shift_K_s', 'noshift_K_s' ],
        #toggle_afm = [ ],
        #toggle_fullscreen = [ 'f', 'alt_K_RETURN', 'alt_K_KP_ENTER', 'K_F11', 'noshift_K_f' ],
        #game_menu = [ 'K_ESCAPE', 'K_MENU', 'K_PAUSE', 'mouseup_3' ],
        #hide_windows = [ 'mouseup_2', 'h', 'noshift_K_h' ],
        #launch_editor = [ 'E', 'shift_K_e' ],
        #dump_styles = [ ],
        #reload_game = [ 'R', 'alt_shift_K_r', 'shift_K_r' ],
        #inspector = [ 'I', 'shift_K_i' ],
        #full_inspector = [ 'alt_shift_K_i' ],
        #developer = [ 'shift_K_d', 'alt_shift_K_d' ],
        #quit = [ ],
        #iconify = [ ],
        #help = [ 'K_F1', 'meta_shift_/' ],
        #choose_renderer = [ 'G', 'alt_shift_K_g', 'shift_K_g' ],
        #progress_screen = [ 'alt_shift_K_p', 'meta_shift_K_p', 'K_F2' ],
        #accessibility = [ "K_a" ],
        # Accessibility.
        #self_voicing = [ 'v', 'V', 'alt_K_v', 'K_v' ],
        #clipboard_voicing = [ 'C', 'alt_shift_K_c', 'shift_K_c' ],
        #debug_voicing = [ 'alt_shift_K_v', 'meta_shift_K_v' ],
        ## Say.
        #rollforward = [ 'mousedown_5', 'K_PAGEDOWN', 'repeat_K_PAGEDOWN' ],
        #dismiss = [ 'mouseup_1', 'K_RETURN', 'K_SPACE', 'K_KP_ENTER', 'K_SELECT' ],
        #dismiss_unfocused = [ ],
        ## Pause.
        #dismiss_hard_pause = [ ],
        ## Focus.
        #focus_left = [ 'K_LEFT', 'repeat_K_LEFT' ],
        #focus_right = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
        #focus_up = [ 'K_UP', 'repeat_K_UP' ],
        #focus_down = [ 'K_DOWN', 'repeat_K_DOWN' ],
        ## Button.
        #button_ignore = [ 'mousedown_1' ],
        #button_select = [ 'mouseup_1', 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ],
        #button_alternate = [ 'mouseup_3' ],
        #button_alternate_ignore = [ 'mousedown_3' ],
        ## Input.
        #input_backspace = [ 'K_BACKSPACE', 'repeat_K_BACKSPACE' ],
        #input_enter = [ 'K_RETURN', 'K_KP_ENTER' ],
        #input_left = [ 'K_LEFT', 'repeat_K_LEFT' ],
        #input_right = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
        #input_up = [ 'K_UP', 'repeat_K_UP' ],
        #input_down = [ 'K_DOWN', 'repeat_K_DOWN' ],
        #input_delete = [ 'K_DELETE', 'repeat_K_DELETE' ],
        #input_home = [ 'K_HOME', 'meta_K_LEFT' ],
        #input_end = [ 'K_END', 'meta_K_RIGHT' ],
        #input_copy = [ 'ctrl_noshift_K_INSERT', 'ctrl_noshift_K_c', 'meta_noshift_K_c' ],
        #input_paste = [ 'shift_K_INSERT', 'ctrl_noshift_K_v', 'meta_noshift_K_v' ],
        #input_jump_word_left = [ 'osctrl_K_LEFT' ],
        #input_jump_word_right = [ 'osctrl_K_RIGHT' ],
        #input_delete_word = [ 'osctrl_K_BACKSPACE' ],
        #input_delete_full = [ 'meta_K_BACKSPACE' ],
        ## Viewport.
        #viewport_leftarrow = [ 'K_LEFT', 'repeat_K_LEFT' ],
        #viewport_rightarrow = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
        #viewport_uparrow = [ 'K_UP', 'repeat_K_UP' ],
        #viewport_downarrow = [ 'K_DOWN', 'repeat_K_DOWN' ],
        #viewport_wheelup = [ 'mousedown_4' ],
        #viewport_wheeldown = [ 'mousedown_5' ],
        #viewport_drag_start = [ 'mousedown_1' ],
        #viewport_drag_end = [ 'mouseup_1' ],
        #viewport_pageup = [ 'K_PAGEUP', 'repeat_K_PAGEUP' ],
        #viewport_pagedown = [ 'K_PAGEDOWN', 'repeat_K_PAGEDOWN' ],
        ## These keys control skipping.
        #skip = [ 'K_LCTRL', 'K_RCTRL' ],
        #stop_skipping = [ ],
        #toggle_skip = [ 'K_TAB' ],
        #fast_skip = [ '>', 'shift_K_PERIOD' ],
        ## Bar.
        #bar_activate = [ 'mousedown_1', 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ],
        #bar_deactivate = [ 'mouseup_1', 'K_RETURN', 'K_KP_ENTER', 'K_SELECT' ],
        #bar_left = [ 'K_LEFT', 'repeat_K_LEFT' ],
        #bar_right = [ 'K_RIGHT', 'repeat_K_RIGHT' ],
        #bar_up = [ 'K_UP', 'repeat_K_UP' ],
        #bar_down = [ 'K_DOWN', 'repeat_K_DOWN' ],
        ## Delete a save.
        #save_delete = [ 'K_DELETE' ],
        ## Draggable.
        #drag_activate = [ 'mousedown_1' ],
        #drag_deactivate = [ 'mouseup_1' ],
        ## Debug console.
        #console = [ 'shift_K_o', 'alt_shift_K_o' ],
        #console_older = [ 'K_UP', 'repeat_K_UP' ],
        #console_newer = [ 'K_DOWN', 'repeat_K_DOWN'],
        ## Director
        #director = [ 'noshift_K_d' ],
        ## Ignored (kept for backwards compatibility).
        #toggle_music = [ 'm' ],
        #viewport_up = [ 'mousedown_4' ],
        #viewport_down = [ 'mousedown_5' ],
        ## Profile commands.
        #performance = [ 'K_F3' ],
        #image_load_log = [ 'K_F4' ],
        #profile_once = [ 'K_F8' ],
        #memory_profile = [ 'K_F7' ],
    #)
