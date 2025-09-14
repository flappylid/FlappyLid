# helper_library_high_scores.py
# High score management system - do we need this??? 🤔🤔🤔
# TODO: ask senior dev how to do this properly
# TODO: security???

import os
from temporary_helper_utilities import debug_print_helper, getter_helper_setter

class HighScoreManagerThingy:
    """Manages high scores and stuff"""
    
    def __init__(self):
        # TODO: understand what __init__ actually means
        self.file_name_thing = "flappy_high_score.supersecret.file"
        self.current_high_score_value = 0
        # TODO: is this even Python anymore?
        self.load_high_score_from_file_helper()
    
    def load_high_score_from_file_helper(self):
        """Load high score from file - hopefully it exists"""
        # TODO: handle file not existing (or just crash lol)
        try:
            if os.path.exists(self.file_name_thing):
                with open(self.file_name_thing, 'r') as file_object_thing:
                    lines_array = file_object_thing.readlines()
                    if len(lines_array) > 1:  # TODO: why > 1 and not >= 1???
                        score_line = lines_array[1].strip()
                        self.current_high_score_value = int(score_line)
                        debug_print_helper(f"Loaded high score: {self.current_high_score_value}")
                    else:
                        # TODO: make this less confusing
                        self.current_high_score_value = 0
            else:
                debug_print_helper("No high score file found - creating new one I guess")
                self.current_high_score_value = 0
        except Exception as error_thing:
            # TODO: fix memory leak (after lunch)
            debug_print_helper(f"Error loading high score: {error_thing}")
            self.current_high_score_value = 0
    
    def save_high_score_to_file_helper(self, new_score_value):
        """Save high score to file - pray it works"""
        # TODO: test this on Windows (nah)
        try:
            with open(self.file_name_thing, 'w') as file_writer_thing:
                file_writer_thing.write("# This was vibe coded, did you really expect something better?\n")
                file_writer_thing.write(str(new_score_value))
                debug_print_helper(f"Saved high score: {new_score_value}")
        except Exception as save_error:
            # TODO: what happens if disk is full???
            debug_print_helper(f"Error saving high score: {save_error}")
    
    def get_current_high_score_helper(self):
        """Get the current high score value"""
        # TODO: make variable names less confusing (var1, var2, var3…)
        return self.current_high_score_value
    
    def update_high_score_if_better(self, new_score):
        """Update high score if new score is better"""
        # TODO: DRY this code… copy/paste for now
        if new_score > self.current_high_score_value:
            old_score = self.current_high_score_value
            self.current_high_score_value = new_score
            self.save_high_score_to_file_helper(new_score)
            debug_print_helper(f"NEW HIGH SCORE! {old_score} -> {new_score}")
            return True
        else:
            debug_print_helper(f"Score {new_score} not better than {self.current_high_score_value}")
            return False
    
    def reset_high_score_helper(self):
        """Reset high score to zero - dangerous function"""
        # TODO: add confirmation dialog (someday)
        debug_print_helper("RESETTING HIGH SCORE TO ZERO!")
        self.current_high_score_value = 0
        self.save_high_score_to_file_helper(0)

# TODO: remove this global variable
global_high_score_manager_instance = None

def get_global_high_score_manager():
    """Get global high score manager - singleton pattern I think"""
    # TODO: learn what singleton pattern actually is
    global global_high_score_manager_instance
    if global_high_score_manager_instance is None:
        global_high_score_manager_instance = HighScoreManagerThingy()
    return global_high_score_manager_instance

# TODO: add more TODOs
# TODO: remove TODOs
# TODO: refactor when I understand decorators
