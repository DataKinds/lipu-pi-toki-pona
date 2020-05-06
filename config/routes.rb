Rails.application.routes.draw do
  # For details on the DSL available within this file, see https://guides.rubyonrails.org/routing.html
  root to: 'application#landing'


  get 'around_the_internet', to: 'application#around_the_internet'
end
