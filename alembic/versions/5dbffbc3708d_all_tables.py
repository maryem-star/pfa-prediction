"""all tables

Revision ID: 5dbffbc3708d
Revises: 
Create Date: 2026-02-19 13:54:51.704832

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '5dbffbc3708d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(100), nullable=False),
    sa.Column('prenom', sa.String(100), nullable=False),
    sa.Column('email', sa.String(150), nullable=True),
    sa.Column('filiere', sa.String(100), nullable=True),
    sa.Column('annee', sa.String(10), nullable=True),
    sa.Column('semestre', sa.String(10), nullable=True),
    sa.Column('photo_url', sa.String(255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(100), nullable=False),
    sa.Column('prenom', sa.String(100), nullable=False),
    sa.Column('email', sa.String(150), nullable=False),
    sa.Column('hashed_password', sa.String(255), nullable=False),
    sa.Column('role', sa.Enum('super_admin', 'admin', 'enseignant', name='roleenum'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('grades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('matiere', sa.String(100), nullable=True),
    sa.Column('note', sa.Float(), nullable=True),
    sa.Column('semestre', sa.String(10), nullable=True),
    sa.Column('annee_academique', sa.String(20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_grades_id'), 'grades', ['id'], unique=False)
    op.create_table('interventions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('type_intervention', sa.String(100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('statut', sa.String(50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interventions_id'), 'interventions', ['id'], unique=False)
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('titre', sa.String(200), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('lu', sa.Boolean(), nullable=True),
    sa.Column('niveau', sa.String(50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_table('predictions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('modele_utilise', sa.String(100), nullable=True),
    sa.Column('probabilite_reussite', sa.Float(), nullable=True),
    sa.Column('statut_couleur', sa.String(20), nullable=True),
    sa.Column('note_predite', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_id'), 'predictions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_predictions_id'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_interventions_id'), table_name='interventions')
    op.drop_table('interventions')
    op.drop_index(op.f('ix_grades_id'), table_name='grades')
    op.drop_table('grades')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_table('students')