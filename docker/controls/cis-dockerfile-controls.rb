# controls/cis_dockerfile_controls.rb
control 'cis-dockerfile-4.1' do
    impact 1.0
    title 'Ensure that the Dockerfile does not use the root user'
    desc 'Do not use the root user in Dockerfile as it can pose security risks.'
  
    describe file('Dockerfile') do
      it { should exist }
      its('content') { should_not match(/^USER root$/) }
    end
  end  