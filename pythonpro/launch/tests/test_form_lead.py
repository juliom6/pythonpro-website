import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains


@pytest.fixture
def email(fake):
    return fake.email()


@pytest.fixture
def create_or_update_with_no_role(mocker):
    return mocker.patch('pythonpro.launch.views.email_marketing_facade.create_or_update_with_no_role')


@pytest.fixture
def resp(client, email, create_or_update_with_no_role, cohort):
    return client.post(reverse('launch:lead_form'), {'email': email}, secure=True)


@pytest.fixture
def invalid_email(email):
    return f'@{email}'


def test_status_code(resp):
    assert 302 == resp.status_code


def test_email_marketing_sucess_integration(resp, email, create_or_update_with_no_role, cohort):
    first_name = email.split('@')[0]
    create_or_update_with_no_role.assert_called_once_with(first_name, email,
                                                          f'turma-{cohort.slug}-semana-do-programador')


@pytest.fixture
def resp_with_error(client, invalid_email, create_or_update_with_no_role):
    return client.post(reverse('launch:lead_form'), {'email': invalid_email}, secure=True)


def test_email_marketing_not_executed_on_error(resp_with_error, create_or_update_with_no_role):
    assert create_or_update_with_no_role.call_count == 0


def test_status_code_error(resp_with_error):
    assert 400 == resp_with_error.status_code


def test_email_field_is_present(resp_with_error):
    dj_assert_contains(resp_with_error, '<input type="email" name="email"', status_code=400)


def test_submmit_button_is_present(resp_with_error):
    dj_assert_contains(resp_with_error, '<button type="submit"', status_code=400)


def test_form_action_is_present(resp_with_error):
    dj_assert_contains(resp_with_error, f'<form method="post" action="{reverse("launch:lead_form")}">', status_code=400)


@pytest.fixture
def resp_with_user(client_with_user, logged_user, cohort, create_or_update_with_no_role):
    return client_with_user.post(reverse('launch:lead_form'), {'email': logged_user.email}, secure=True)


def test_user_first_name(resp_with_user, logged_user, create_or_update_with_no_role, cohort):
    create_or_update_with_no_role.assert_called_once_with(
        logged_user.first_name,
        logged_user.email,
        f'turma-{cohort.slug}-semana-do-programador',
        id=logged_user.id
    )
