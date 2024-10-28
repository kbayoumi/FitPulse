from .auth.signup import signup_bp
from .auth.signin import signin_bp  # Import the signin blueprint
from .auth.logout import logout_bp  # Import the logout blueprint
from .admin.auth import admin_auth_bp  # Import the admin auth blueprint
from .admin.exercisescontroller import exercises_bp  # Import the exercises management blueprint
from .admin.storecontroller import managestore_bp  # Import the store management blueprint
from .admin.trainerscontroller import trainers_bp  # Import the trainers management blueprint
from .diet.dietplanscontroller import dietplans_bp  # Import diet plans management blueprint
from .careers.routes import careers_bp  # Import the careers blueprint
from .store.routes import store_bp
from .recipes.recipescontroller import recipes_bp
from .trainer.routes import trainer_bp
from .profile.profilecontroller import profile_bp
from .workouts.workoutcontroller import workouts_bp
from .workouts.workoutdayscontroller import workoutdays_bp  
from .calenders.callendercontroller import calender_bp  # Import the calender blueprint
from .challenges.challengecontroller import challenges_bp  # Import the challenges blueprint
from .tools.toolscontroller import tools_bp  # Import the tools blueprint


def register_routes(app):
    # Register authentication blueprints
    app.register_blueprint(signup_bp)
    app.register_blueprint(signin_bp)
    app.register_blueprint(logout_bp)
    
    # Register admin-related blueprints
    app.register_blueprint(admin_auth_bp)  # Admin auth blueprint
    app.register_blueprint(managestore_bp)  # Store management blueprint
    app.register_blueprint(exercises_bp)  # Exercises management blueprint
    app.register_blueprint(trainers_bp)  # Trainers management blueprint

    # Register other blueprints
    app.register_blueprint(dietplans_bp)  # Diet plans blueprint
    app.register_blueprint(careers_bp)  # Register careers blueprint
    app.register_blueprint(store_bp)  # Register store blueprint
    
    app.register_blueprint(recipes_bp)  # Register recipes blueprint

    app.register_blueprint(trainer_bp)  # Register trainer blueprint
    
    app.register_blueprint(profile_bp)  # Register profile blueprint
    
    app.register_blueprint(workouts_bp)  # Register workouts blueprint
    
    app.register_blueprint(workoutdays_bp)  # Register workout days blueprint  \
        
    app.register_blueprint(calender_bp)  # Register calender blueprint 
    
    app.register_blueprint(challenges_bp)  # Register challenges blueprint
    
    app.register_blueprint(tools_bp)  # Register tools blueprint